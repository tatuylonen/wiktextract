# Simple WikiMedia markup (WikiText) syntax parser
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import enum

@enum.unique
class NodeKind(enum.Enum):
    ROOT = enum.auto(),
    LEVEL2 = enum.auto(),
    LEVEL3 = enum.auto(),
    LEVEL4 = enum.auto(),
    LEVEL5 = enum.auto(),
    LEVEL6 = enum.auto(),
    ITALIC = enum.auto(),
    BOLD = enum.auto(),
    BOLD_ITALIC = enum.auto(),
    HLINE = enum.auto(),
    LIST_ITEM = enum.auto(),  # args = token for this item
    PREFORMATTED = enum.auto(),  # Preformatted inline text
    PREBLOCK = enum.auto(),  # Preformatted block
    PRERAW = enum.auto(),  # Preformatted text where specials not interpreted
    HTML = enum.auto(),
    INTERNAL_LINK = enum.auto(),
    TEMPLATE = enum.auto(),
    TEMPLATEVAR = enum.auto(),
    PARSERFN = enum.auto(),
    URL = enum.auto(),
    MEDIA = enum.auto(),
    TABLE = enum.auto(),
    TABLE_CAPTION = enum.auto(),
    TABLE_HEADER_ROW = enum.auto(),
    TABLE_HEADER_CELL = enum.auto(),
    TABLE_ROW = enum.auto(),
    TABLE_CELL = enum.auto(),
    # XXX <ref ...> and <references />
    # XXX -{ ... }- syntax, see
    # https://www.mediawiki.org/wiki/Writing_systems/Syntax ??

    # __NOTOC__


HAVE_ARGS_KINDS = (
    NodeKind.INTERNAL_LINK,
    NodeKind.TEMPLATE,
    NodeKind.TEMPLATEVAR,
    NodeKind.PARSERFN,
    NodeKind.URL,
    NodeKind.MEDIA,
)


# Node kinds that generate an error if they have not been properly closed.
MUST_CLOSE_KINDS = (
    NodeKind.ITALIC,
    NodeKind.BOLD_ITALIC,
    NodeKind.BOLD,
    NodeKind.PREFORMATTED,
    NodeKind.PREBLOCK,
    NodeKind.PRERAW,
    NodeKind.HTML,
    NodeKind.INTERNAL_LINK,
    NodeKind.TEMPLATE,
    NodeKind.TEMPLATEVAR,
    NodeKind.PARSERFN,
    NodeKind.URL,
    NodeKind.MEDIA,
    NodeKind.TABLE,
)


class WikiNode(object):
    """Node in the parse tree for WikiMedia text."""
    __slots__ = (
        "kind",
        "args",
        "attrs",
        "children",
        "loc",
    )

    def __init__(self, kind, loc):
        assert isinstance(kind, NodeKind)
        assert isinstance(loc, int)
        self.kind = kind
        self.args = []  # List of lists
        self.attrs = {}
        self.children = []   # list of str and WikiNode
        self.loc = loc

    def __str__(self):
        return "<{}({}) {}>".format(self.kind.name,
                                    self.args if isinstance(self.args, str)
                                    else ", ".join(map(repr, self.args)),
                                    ", ".join(map(repr, self.children)))

    def __repr__(self):
        return self.__str__()


class ParseCtx(object):
    """Parsing context for parsing WikiMedia text.  This contains the parser
    stack, which also implicitly contains all text parsed so far and the
    partial parse tree."""
    __slots__ = (
        "stack",
        "linenum",
        "beginning_of_line",
        "errors",
        "pagetitle",
        "nowiki",
    )

    def __init__(self, pagetitle):
        assert isinstance(pagetitle, str)
        top_node = WikiNode(NodeKind.ROOT, 0)
        top_node.args.append(pagetitle)
        self.stack = [top_node]
        self.linenum = 1
        self.beginning_of_line = True
        self.errors = []
        self.pagetitle = pagetitle
        self.nowiki = False

    def push(self, kind):
        assert isinstance(kind, NodeKind)
        node = WikiNode(kind, self.linenum)
        top = self.stack[-1]
        top.children.append(node)
        self.stack.append(node)
        return node

    def pop(self, warn_unclosed):
        """Pops a node from the stack.  If the node has arguments, this moves
        remaining children of the node into its arguments.  If ``warn_unclosed``
        is True, this warns about nodes that should be explicitly closed
        not having been closed."""
        assert warn_unclosed in (True, False)
        node = self.stack[-1]
        # If the node has arguments, move remamining children to be the last
        # argument
        if node.kind in HAVE_ARGS_KINDS:
            node.args.append(node.children)
            node.children = []
        if warn_unclosed and node.kind in MUST_CLOSE_KINDS:
            self.error("format {} not properly closed, started on line {}"
                       "".format(node.kind.name, node.loc))
        self.stack.pop()

    def have(self, kind):
        """Returns True if any node on the stack is of the given kind."""
        assert isinstance(kind, NodeKind)
        for node in self.stack:
            if node.kind == kind:
                return True
        return False

    def error(self, msg, loc=None):
        """Prints a parsing error message and records it in self.errors."""
        if loc is None:
            loc = self.linenum
        msg = "{}:{}: ERROR: {}".format(self.pagetitle, loc, msg)
        print(msg, file=sys.stderr)
        self.errors.append(msg)


def text_fn(ctx, text):
    top = ctx.stack[-1]
    top.children.append(text)

def hline_fn(ctx, token):
    ctx.push(NodeKind.HLINE)
    ctx.pop(True)

# Maps subtitle token to its kind
subtitle_to_kind = {
    "==": NodeKind.LEVEL2,
    "===": NodeKind.LEVEL3,
    "====": NodeKind.LEVEL4,
    "=====": NodeKind.LEVEL5,
    "======": NodeKind.LEVEL6,
}

# Maps subtitle node kind to its level.  Keys include all title/subtitle nodes.
kind_to_level = { v: len(k) for k, v in subtitle_to_kind.items() }
kind_to_level[NodeKind.ROOT] = 1

def subtitle_start_fn(ctx, token):
    assert isinstance(ctx, ParseCtx)
    assert isinstance(token, str)
    kind = subtitle_to_kind[token[1:]]
    level = kind_to_level[kind]

    # Keep popping subtitles and other formats until the next subtitle
    # is of a higher level.
    while True:
        node = ctx.stack[-1]
        if kind_to_level.get(node.kind, 99) < level:
            break
        ctx.pop(True)

    # Push the subtitle node.  Subtitle start nodes are guaranteed to have
    # a close node, though the close node could have an incorrect level.
    ctx.push(kind)

def subtitle_end_fn(ctx, token):
    assert isinstance(ctx, ParseCtx)
    assert isinstance(token, str)
    kind = subtitle_to_kind[token[1:]]

    # Keep popping formats until we get to the subtitle node
    while True:
        node = ctx.stack[-1]
        if node.kind in kind_to_level:
            break
        ctx.pop(True)

    # Move children of the subtitle node to be its first argument.
    node = ctx.stack[-1]
    if node.kind != kind:
        ctx.error("subtitle start and end markers level mismatch")
    node.args.append(node.children)
    node.children = []

def bolditalic_fn(ctx, token):
    if ctx.have(NodeKind.BOLD_ITALIC):
        # Close current formatting
        ctx.pop(False)
    else:
        # Push new formatting node
        ctx.push(NodeKind.BOLD_ITALIC)

def italic_fn(ctx, token):
    if ctx.have(NodeKind.ITALIC):
        # Close current formatting
        ctx.pop(False)
    else:
        # Push new formatting node
        ctx.push(NodeKind.ITALIC)

def bold_fn(ctx, token):
    if ctx.have(NodeKind.BOLD):
        # Close current formatting
        ctx.pop(False)
    else:
        # Push new formatting node
        ctx.push(NodeKind.BOLD)

def preformatted_fn(ctx, token):
    top = ctx.stack[-1]
    if top != NodeKind.PREFORMATTED:
        ctx.push(NodeKind.PREFORMATTED)

def ilink_start_fn(ctx, token):
    ctx.push(NodeKind.INTERNAL_LINK)

def ilink_end_fn(ctx, token):
    if not ctx.have(NodeKind.INTERNAL_LINK):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.INTERNAL_LINK:
            ctx.pop(False)
            break
        if node.kind in kind_to_level:
            break  # Never pop past section header
        ctx.pop(True)

def elink_start_fn(ctx, token):
    ctx.push(NodeKind.URL)

def elink_end_fn(ctx, token):
    if not ctx.have(NodeKind.URL):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.URL:
            ctx.pop(False)
            break
        if node.kind in kind_to_level:
            break  # Never pop past section header
        ctx.pop(True)

def url_fn(ctx, token):
    node = ctx.stack[-1]
    if node.kind == NodeKind.URL:
        text_fn(ctx, token)
        return
    node = ctx.push(NodeKind.URL)
    node.children.append(token)
    ctx.pop(False)

def templarg_start_fn(ctx, token):
    """Handler for template argument reference start token {{{."""
    ctx.push(NodeKind.TEMPLATEVAR)


def templarg_end_fn(ctx, token):
    """Handler for template argument reference end token }}}."""
    if not ctx.have(NodeKind.TEMPLATEVAR):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TEMPLATEVAR:
            ctx.pop(False)
            break
        if node.kind in kind_to_level:
            break  # Never pop past section header
        ctx.pop(True)


def templ_start_fn(ctx, token):
    """Handler for template start token {{."""
    ctx.push(NodeKind.TEMPLATE)


def templ_end_fn(ctx, token):
    """Handler function for template end token }}."""
    if not ctx.have(NodeKind.TEMPLATE) and not ctx.have(NodeKind.PARSERFN):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind in (NodeKind.TEMPLATE, NodeKind.PARSERFN):
            ctx.pop(False)
            break
        if node.kind in kind_to_level:
            break  # Never pop past section header
        ctx.pop(True)


def colon_fn(ctx, token):
    """Handler for a special colon (:) within a template call.  This indicates
    that it is actually a parser function call."""
    top = ctx.stack[-1]

    # Unless we are in the first argument of a template, treat a colon that is
    # not at the beginning of a
    if top.kind != NodeKind.TEMPLATE or top.args:
        text_fn(ctx, token)
        return

    # Colon in the first argument of {{name:...}} turns it into a parser
    # function call.
    top.kind = NodeKind.PARSERFN
    top.args.append(top.children)
    top.children = []


def table_start_fn(ctx, token):
    """Handler for table start token {|."""
    ctx.push(NodeKind.TABLE)


def table_caption_fn(ctx, token):
    """Handler for table caption token |+."""
    if not ctx.have(NodeKind.TABLE):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TABLE:
            break
        ctx.pop(True)
    ctx.push(NodeKind.TABLE_CAPTION)


def table_hdr_cell_fn(ctx, token):
    """Handler function for table header row cell separator ! or !!."""
    if not ctx.have(NodeKind.TABLE):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TABLE_HEADER_ROW:
            break
        if node.kind == NodeKind.TABLE:
            ctx.push(NodeKind.TABLE_HEADER_ROW)
            break
        ctx.pop(True)
    ctx.push(NodeKind.TABLE_HEADER_CELL)


def table_row_fn(ctx, token):
    """Handler function for table row separator |-."""
    if not ctx.have(NodeKind.TABLE):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TABLE:
            break
        ctx.pop(True)
    ctx.push(NodeKind.TABLE_ROW)


def table_row_cell_fn(ctx, token):
    """Handler function for table row cell separator."""
    if not ctx.have(NodeKind.TABLE):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TABLE_ROW:
            break
        if node.kind == NodeKind.TABLE:
            ctx.push(NodeKind.TABLE_ROW)
            break
        ctx.pop(True)
    ctx.push(NodeKind.TABLE_CELL)


def vbar_fn(ctx, token):
    """Handler function for vertical bar |.  The interpretation of
    the vertical bar depends on context; it can separate arguments to
    templates, template argument references, links, etc, and it can
    also separate table row cells."""
    node = ctx.stack[-1]
    if node.kind in HAVE_ARGS_KINDS:
        node.args.append(node.children)
        node.children = []
        return

    table_row_cell_fn(ctx, token)


def table_end_fn(ctx, token):
    """Handler function for end of a table token |}."""
    if not ctx.have(NodeKind.TABLE):
        text_fn(ctx, token)
        return
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.TABLE:
            break
        if node.kind in kind_to_level:
            break  # Always break before section headers
    ctx.pop(False)


def list_fn(ctx, token):
    """Handles various tokens that start unordered or ordered list items,
    description list items, or indented lines."""
    top = ctx.stack[-1]

    # A colon inside a template means it is a parser function call.  We use
    # colon_fn() to handle that kind of colon.
    if token == ":" and top.kind == NodeKind.TEMPLATE:
        colon_fn(ctx, token)
        return

    # An external link
    if top.kind in (NodeKind.INTERNAL_LINK, NodeKind.URL):
        text_fn(ctx, token)
        return

    # Pop any lower-level list items
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.LIST_ITEM and len(node.args) < len(token):
            break
        if node.kind in kind_to_level:
            break  # Always break before section header
        if node.kind in (NodeKind.HTML, NodeKind.TEMPLATE,
                         NodeKind.TEMPLATEVAR, NodeKind.PARSERFN,
                         NodeKind.TABLE,
                         NodeKind.TABLE_HEADER_ROW,
                         NodeKind.TABLE_HEADER_CELL,
                         NodeKind.TABLE_ROW,
                         NodeKind.TABLE_CELL):
            break
        ctx.pop(True)
    node = ctx.push(NodeKind.LIST_ITEM)
    node.args = token


def tag_fn(ctx, token):
    """Handler function for tokens that look like HTML tags and their end
    tags.  This includes various built-in tags that aren't actually
    HTML, including <nowiki>."""
    # Try to parse it as a start tag
    m = re.match(r"<\s*([-a-zA-Z0-9]+)\s*(/?)\s*>", token)  # XXX attrs
    if m:
        # This is a start tag
        name = m.group(1)
        also_end = m.group(2) == "/"
        top = ctx.stack[-1]
        name = name.lower()
        # Handle <nowiki> start tag
        if name == "nowiki":
            if not also_end:
                ctx.nowiki = True
            return

        # Handle other start tag
        node = ctx.push(NodeKind.HTML)
        node.args.append(name)
        # XXX handle attrs

        # If it is also an end tag, pop it immediately.
        if also_end:
            ctx.pop(False)
        return

    # Since it was not a start tag, it should be an end tag
    m = re.match(r"<\s*/\s*([-a-zA-Z0-9]+)\s*>", token)
    assert m  # If fails, then mismatch between regexp here and tokenization
    name = m.group(1)
    top = ctx.stack[-1]
    name = name.lower()
    if name == "nowiki":
        # Handle </nowiki> end tag
        if ctx.nowiki:
            ctx.nowiki = False
        else:
            ctx.error("unexpected </nowiki>")
        return

    # Handle other end tag
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.HTML and node.args[0] == name:
            ctx.pop(False)
            break
        if node.kind in kind_to_level:
            break
        ctx.pop(True)
    return


# Regular expression for matching a token in WikiMedia text
token_re = re.compile(r"(?m)^(={2,6})\s*(([^=)|=[^=])+?)\s*(={2,6})\s*$|"
                      r"'''''|"
                      r"'''|"
                      r"''|"
                      r"^ |"   # Space at beginning means preformatted
                      r"\[\[|"
                      r"\]\]|"
                      r"\[|"
                      r"\]|"
                      r"\{\{\{|"
                      r"\}\}\}|"
                      r"\{\{|"
                      r"\}\}|"
                      r"\{\|"
                      r"\|\}|"
                      r"\|\+|"
                      r"\|-|"
                      r"^!|"
                      r"!!|"
                      r"\||"
                      r"^----+|"
                      r"^[-*:;#]+\s*|"
                      r"<\s*[-a-zA-Z0-9]+\s*/?\s*>|"  # XXX attrs
                      r"<\s*/\s*[-a-zA-Z0-9]+\s*>|"
                      r"https?://[a-zA-Z0-9.]+|"
                      r":")

# Dictionary mapping fixed form tokens to handler functions.
tokenops = {
    "'''''": bolditalic_fn,
    "'''": bold_fn,
    "''": italic_fn,
    " ": preformatted_fn,
    "[[": ilink_start_fn,
    "]]": ilink_end_fn,
    "[": elink_start_fn,
    "]": elink_end_fn,
    "{{{": templarg_start_fn,
    "}}}": templarg_end_fn,
    "{{": templ_start_fn,
    "}}": templ_end_fn,
    "{|": table_start_fn,
    "|}": table_end_fn,
    "|+": table_caption_fn,
    "!-": table_hdr_cell_fn,
    "|-": table_row_fn,
    "||": table_row_cell_fn,
    "|": vbar_fn,
}


def token_iter(text):
    """Tokenizes MediaWiki page content.  This yields (is_token, text) for
    each token.  ``is_token`` is False for text and True for other tokens."""
    assert isinstance(text, str)
    pos = 0
    for m in re.finditer(token_re, text):
        start = m.start()
        if pos != start:
            yield False, text[pos:start]
        pos = m.end()
        token = m.group(0)
        if token.startswith("=="):
            yield True, "<" + m.group(1)
            for x in token_iter(m.group(2)):
                yield x
            yield True, ">" + m.group(4)
        else:
            yield True, token
    if pos != len(text):
        yield False, text[pos:]


def parse_with_ctx(pagetitle, text):
    """Parses a Wikitext document into a tree.  This returns a WikiNode object
    that is the root of the parse tree and the parse context."""
    assert isinstance(pagetitle, str)
    assert isinstance(text, str)
    # Create parse context.  This also pushes a ROOT node on the stack.
    ctx = ParseCtx(pagetitle)
    # Process all tokens from the input.
    for is_token, token in token_iter(text):
        assert isinstance(token, str)
        top = ctx.stack[-1]
        if (not is_token or
            (ctx.nowiki and
             not re.match(r"(?i)<\s*/\s*nowiki\s*>", token))):
            if is_token:
                # Remove the artificially added prefix from subtitle tokens
                if token.startswith("<=="):
                    token = token[1:]
                elif token.startswith(">=="):
                    token = token[1:]
            text_fn(ctx, token)
        else:
            if token in tokenops:
                tokenops[token](ctx, token)
            elif token.startswith("<=="):  # Note: < added by tokenizer
                subtitle_start_fn(ctx, token)
            elif token.startswith(">=="):  # Note: > added by tokenizer
                subtitle_end_fn(ctx, token)
            elif token.startswith("----"):
                hline_fn(ctx, token)
            elif token.startswith("<") and len(token):
                tag_fn(ctx, token)
            elif ctx.beginning_of_line and re.match(r"[-*:;#]+", token):
                list_fn(ctx, token)
            elif re.match(r"https?://.*", token):
                url_fn(ctx, token)
            else:
                text_fn(ctx, token)
        ctx.linenum += len(list(re.finditer("\n", token)))
        ctx.beginning_of_line = token.endswith("\n")
        if ctx.beginning_of_line:
            # Some nodes are automatically popped on newline
            if ctx.stack[-1].kind in (NodeKind.PREFORMATTED,):
                ctx.pop()
    while True:
        node = ctx.stack[-1]
        if node.kind == NodeKind.ROOT:
            break
        ctx.pop(True)
    assert len(ctx.stack) == 1
    return ctx.stack[0], ctx


def parse(pagetitle, text):
    """Parse a wikitext document into a tree.  This returns a WikiNode
    object that is the root of the parse tree and the parse context."""
    assert isinstance(pagetitle, str)
    assert isinstance(text, str)
    tree, ctx = parse_with_ctx(pagetitle, text)
    return tree


def print_tree(tree, indent):
    """Prints the parse tree for debugging purposes."""
    assert isinstance(tree, (WikiNode, str))
    assert isinstance(indent, int)
    if isinstance(tree, str):
        print("{}{}".format(" " * indent, repr(tree)))
        return
    print("{}{} {}".format(" " * indent, tree.kind.name, tree.args))
    for child in tree.children:
        print_tree(child, indent + 2)


# Very simple test:
# data = open("pages/Words/ho/horse.txt", "r").read()
# tree = parse("horse", data)
# print_tree(tree, 0)
