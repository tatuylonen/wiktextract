# Definitions of HTML tags that are allowed in WikiText and which contexts
# they can occur in, whether they need ends tags, and whether they are
# implicitly closed by some other tags.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org


# HTML tags that are allowed in input.  These are generated as HTML nodes
# to distinguish them from text.  Note that only the tags themselves are
# made HTML nodes to distinguisth them from plain text ("<" in returned plain
# text should be rendered as "&lt;" in HTML).  This does not try to match
# HTML start tags against HTML end tags, and only the tag itself is included
# as children of HTML nodes.
#
# The value is a list (acceptable_parents, permitted_content), based on
# the tables in HTML elements under
# https://developer.mozilla.org/en-US/docs/Web/HTML
# (and arbitrarily selected for non-HTML elements).  Acceptable_parents
# contains a list of tags and content types used in permitted_content
# ("flow", "text", or tag name).  Having "flow" as permitted content implies
# "phrasing and "text", and "phrasing" implies "text".
#
# no-end-tag set to true means the tag should not have an end tag.
# close-next lists tags that automatically closes this tag.  Closing a
# parent tag will also silently close them.  Otherwise a missing end tag
# results in an error message.
ALLOWED_HTML_TAGS = {
    "abbr": {
        "parents": ["phrasing"],
        "content": ["flow"]},
    "b": {
        "parents": ["phrasing"],
        "content": ["flow"]},
    "big": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "bdi": {
        "parents": ["phrasing"],
        "content": ["flow"]},
    "bdo": {
        "parents": ["phrasing"],
        "content": ["flow"]},
    "blockquote": {
        "parents": ["flow"],
        "content": ["flow"]},
    "br": {
        "parents": ["phrasing"],
        "no-end-tag": True,
        "content": []},
    "caption": {
        "parents": ["table"],
        "content": ["flow"]},
    "center": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "cite": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "code": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "data": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "dd": {
        "parents": ["dl", "div"],
        "close-next": ["dd", "dt"],
        "content": ["flow"]},
    "del": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "dfn": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "div": {
        "parents": ["flow", "dl"],
        "content": ["flow"]},
    "dl": {
        "parents": ["flow"],
        "content": []},
    "dt": {
        "parents": ["dl", "div"],
        "close-next": ["dd", "dt"],
        "content": ["flow"]},
    "em": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "font": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "gallery": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h1": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h2": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h3": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h4": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h5": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "h6": {
        "parents": ["flow"],
        "content": ["phrasing"]},
    "hr": {
        "parents": ["flow"],
        "no-end-tag": True,
        "content": []},
    "i": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    # From ImageMap extension, see
    # https://www.mediawiki.org/wiki/Extension:ImageMap
    "imagemap": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "includeonly": {
        "parents": ["*"],
        "content": ["*"]},
    # From InputBox extension, see
    # https://www.mediawiki.org/wiki/Extension:InputBox
    "inputbox": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "ins": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "kbd": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "li": {
        "parents": ["ul", "ol", "menu"],
        "close-next": ["li"],
        "content": ["flow"]},
    "math": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "mark": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "noinclude": {
        "parents": ["*"],
        "content": ["*"]},
    "ol": {
        "parents": ["flow"],
        "content": ["flow"]},
    "onlyinclude": {
        "parents": ["*"],
        "content": ["*"]},
    "p": {
        "parents": ["flow"],
        "close-next": ["p", "address", "article", "aside", "blockquote",
                       "div", "dl", "fieldset", "footer", "form", "h1", "h2",
                       "h3", "h4", "h5", "h6", "header", "hr", "menu", "nav",
                       "ol", "pre", "section", "table", "ul"],
        "content": ["phrasing"]},
    "q": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "rb": {
        "parents": ["ruby"],
        "close-next": ["rt", "rtc", "rp", "rb"],
        "content": ["phrasing"]},
    "ref": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "references": {
        "parents": ["flow"],
        "no-end-tag": True,
        "content": []},
    "rp": {
        "parents": ["ruby"],
        "close-next": ["rt", "rtc", "rp", "rb"],
        "content": ["text"]},
    "rt": {
        "parents": ["ruby", "rtc"],
        "close-next": ["rt", "rtc", "rp", "rb"],
        "content": ["phrasing"]},
    "rtc": {
        "parents": ["ruby"],
        "close-next": ["rt", "rtc", "rb"],
        "content": ["phrasing"]},
    "ruby": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "s": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "samp": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "small": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "span": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "strike": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "strong": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "sub": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "sup": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "syntaxhighlight": {
        "parents": ["flow"],
        "content": ["flow"],
    },
    "table": {
        "parents": ["flow"],
        "content": []},
    "tbody": {
        "parents": ["table"],
        "close-next": ["thead", "tbody", "tfoot"],
        "content": []},
    "td": {
        "parents": ["tr"],
        "close-next": ["th", "td"],
        "content": ["flow"]},
    # From TemplateStyles extension; see
    # https://www.mediawiki.org/wiki/Extension:TemplateStyles
    "templatestyles": {
        "parents": ["phrasing"],
        "no-end-tag": True,
        "content": []},
    "tfoot": {
        "parents": ["table"],
        "close-next": ["thead", "tbody", "tfoot"],
        "content": []},
    "th": {
        "parents": ["tr"],
        "close-next": ["th", "td"],
        "content": ["flow"]},
    "thead": {
        "parents": ["table"],
        "close-next": ["thead", "tbody", "tfoot"],
        "content": []},
    "time": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "tr": {
        "parents": ["table", "thead", "tfoot", "tbody"],
        "close-next": ["tr"],
        "content": []},
    "tt": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "u": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "ul": {
        "parents": ["flow"],
        "content": ["flow"]},
    "var": {
        "parents": ["phrasing"],
        "content": ["phrasing"]},
    "wbr": {
        "parents": ["phrasing"],
        "no-end-tag": True,
        "content": []},
}
