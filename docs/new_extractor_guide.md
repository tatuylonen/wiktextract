# Create new Wiktionary extractor guide

## Learn wikitext

Read document [Help:Wikitext](https://en.wikipedia.org/wiki/Help:Wikitext) to learn the basic syntax of wikitext.

More MediaWiki documents:
- [Help:A quick guide to templates](https://en.wikipedia.org/wiki/Help:A_quick_guide_to_templates)
- [Help:Template](https://en.wikipedia.org/wiki/Help:Template)
- [Help:Transclusion](https://en.wikipedia.org/wiki/Help:Transclusion)
- [Help:Extension:ParserFunctions](https://www.mediawiki.org/wiki/Help:Extension:ParserFunctions)
- [Help:Magic words](https://www.mediawiki.org/wiki/Help:Magic_words)
- [Extension:Scribunto/Lua reference manual](https://www.mediawiki.org/wiki/Extension:Scribunto/Lua_reference_manual)

## Read Wiktionary entry layout document

Every Wiktionary has their unique page layout, they usually have a document page of the layout and other rules. For example, here is English Wiktionary's document: [Wiktionary:Entry layout](https://en.wiktionary.org/wiki/Wiktionary:Entry_layout). After reading the layout document, try edit some pages or create a new page to test whether you have grasped Wiktionary editing. Writing Wiktionary extractor is like a reversed editing process.

## Learn wikitextprocessor parser API

[wikitextprocessor](https://github.com/tatuylonen/wikitextprocessor) is a wikitext parser that takes in wikitext and generates a parse-tree.

Here is a simplified wikitext of English Wiktionary page [dictionary](https://en.wiktionary.org/wiki/dictionary) and we'll use wikitextprocessor library to parse it:

```wikitext
==English==
===Noun===
# {{lb|en|computing}} An [[associative array]]
```

```python
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig, WiktextractContext

wtp = Wtp(db_path="db_path", lang_code="en")
conf = WiktionaryConfig(
    dump_file_lang_code="en", capture_language_codes=None
)
wxr = WiktextractContext(wtp, conf)
wxr.wtp.start_page("dictionary")
root = wtp.parse(
    """==English==
===Noun===
# {{lb|en|computing}} An [[associative array]]"""
)
```

The level 3 Part of Speech (POS) node(`===Noun===`) is the child of level 2 language node(`==English==`):

```python
from wikitextprocessor.parser import print_tree

print_tree(root)
# ROOT [['']]
#  LEVEL2 [['English']]
#    '\n'
#    LEVEL3 [['Noun']]
#      '\n'
#      LIST #
#        LIST_ITEM #
#          ' '
#          TEMPLATE [['lb'], ['en'], ['computing']]
#          ' An '
#          LINK [['associative array']]
print(root.children)
# [<LEVEL2(['English']){} '\n', <LEVEL3(['Noun']){} '\n', <LIST(#){} <LIST_ITEM(#){} ' ', <TEMPLATE(['lb'], ['en'], ['computing']){} >, ' An ', <LINK(['associative array']){} >>>>>]
```

Child node can be located with these APIs: `WikiNode.find_child()`, `WikiNode.find_child_recursively()`, `WikiNode.invert_find_child()`, `WikiNode.find_html()`, `WikiNode.find_html_recursively()`. Parser API source code: [src/wikitextprocessor/parser.py](https://github.com/tatuylonen/wikitextprocessor/blob/main/src/wikitextprocessor/parser.py)

```python
from wikitextprocessor import NodeKind

for t_node in root.find_child_recursively(NodeKind.TEMPLATE):
    pass
```

`NodeKind` is a [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag) class, these flags can be combined:

```python
for node in root.find_child(NodeKind.BOLD | NodeKind.LINK):
    pass
```

Template can be expanded like this:

```python
expanded_node = wxr.wtp.parse(
    wxr.wtp.node_to_wikitext(t_node), expand_all=True
)
```

`Wtp.parse()` accepts wikitext input not `WikiNode`, so we need to convert a parsed node to its wikitext using `Wtp.node_to_wikitext()`.

MediaWiki's special page [Special:ExpandTemplates](https://en.wiktionary.org/wiki/Special:ExpandTemplates) can be used to obtain the expanded wikitext of a template, this is very helpful when writing extractor for template.

`clean_node()` can be used to convert node to text:

```python
from wiktextract.page import clean_node

print(clean_node(wxr, None, t_node))
# "(computing)"
```

The second argument of `clean_node()` is for saving [category links](https://en.wikipedia.org/wiki/Help:Wikitext#Categories), it can be dictionary or pydantic model or `None`. If it's not `None`, a list of strings will be added to the "categories" field of pydantic model or dictionary.

Template name and parameters are available as properties of `TemplateNode` class:

```python
print(t_node.template_name)
# "lb"
print(t_node.template_parameters)
# {1: 'en', 2: 'computing'}
```

The `TemplateNode.template_parameters` dictionary values can't be used directly. If you want to find a node in a template parameter, the value must be parsed:

```python
parsed_arg = wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value), expand_all=True)
```

If text string is needed, `clean_node()` should be used:

```python
clean_node(wxr, None, t_node.template_parameters[1])
```

`LevelNode.find_content()` is used to find node inside the level node but not the child nodes:

```python
root = wxr.wtp.parse("=={{lang|en}}==\ntext in child node")
for t_node in root.find_content(NodeKind.TEMPLATE):
    pass
```

Nodes inside level node wikitext are in `LevelNode.largs` list:

```python
root = wxr.wtp.parse("==English==\ntext in child node")
for level_node in root.find_child(NodeKind.LEVEL2):
    print(clean_node(wxr, None, level_node.largs))
    # "English"
```

For description lists, term nodes are in the `WikiNode.children` attribute, definition nodes are in the `WikiNode.definition` attribute:

```python
root = wxr.wtp.parse("; term : definition")
list_item = next(root.find_child_recursively(NodeKind.LIST_ITEM))
print(list_item.children)
# [' term ']
print(list_item.definition)
# [' def']
```

`HTMLNode` has a `tag` property for the tag name, and `attrs` dictionary for HTML attributes:

```python
root = wxr.wtp.parse('<span class="span_class">text</span>')
for span_tag in root.find_html("span"):
    print(span_tag.tag)
    # "span"
    print(span_tag.attrs)
    # {"class": "span_class"}
```

List type can be distinguished by checking the `WikiNode.sarg` attribute:

```python
root = wxr.wtp.parse("""===Noun===
# gloss
#: {{ux|en|example sentence}}
#* {{quote-book|en|example sentence}}
## child gloss
##: {{ux|en|example}}""")

first_list_item = next(root.find_child_recursively(NodeKind.LIST_ITEM))
print(first_list_item.sarg)
# "#"
for child_list in first_list_item.find_child(NodeKind.LIST):
    print(child_list.sarg)
    # "#:", "#*", "##" or "##:"
    if child_list.sarg.startswith("#") and child_list.sarg.endswith((":", "*")):
        # extract example or linkage
    elif child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
        for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
            # extract nested gloss
```

## Choose which namespaces to use from dump file

MediWiki pages are grouped in collections called "[namespaces](https://www.mediawiki.org/wiki/Help:Namespaces)". By default, "Main", "Template", "Module" namespaces are used, their corresponding ids are `0`, `10`, `828`. "Main" namespace contains word pages, "Module" namespace contain Lua code used in templates. If pages in other namespaces are needed, they should be added in a `config.json` file, this JSON file can override some default attributes of the [`WiktionaryConfig`](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/config.py) class. For example, [here](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/data/fr/config.json) is the JSON file for French Wiktionary. All namespace names and ids can be found at the start of [dump file](https://dumps.wikimedia.org/backup-index.html)("*-pages-articles.xml.bz2" file). You may need to update the [namespace data file](https://github.com/tatuylonen/wikitextprocessor/tree/main/src/wikitextprocessor/data) in wikitextprocessor package, these files should be updated using this [script](https://github.com/tatuylonen/wikitextprocessor/blob/main/tools/get_namespaces.py).

You could start with the default three namespaces than add the required namespace later when you encounter a Lua error or decide to extract pages in a namespace.

## Pre-expand section templates

Some Wiktionary editions use templates to expand to section wikitext or HTML tags, these templates need to be expanded before parsing the page wikitext to nodes. Skip this step if the new Wiktionary doesn't have this problem.

Section templates must be expanded to section wikitext before being parsed, otherwise they'll still be parsed as template node and nodes under a section will not be parsed as section child.

### Section template expands to wikitext

Write a `analyze_template()` in file "analyze_template.py", this function checks all template pages and return `True` if the template need pre-expand. Example [file](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/nl/analyze_template.py) of Dutch Wiktionary.

### Section template expands to HTML

Because we relay on section nodes to distinguish their level number and group child nodes, if an edition uses HTML tags, we lost both information and also unable to know which HTML tag is the start of a section.

Template body can be overridden in wikitext to solve this problem. Example [override file](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/data/overrides/id.json) for Indonesian Wiktionary. The new line character `\n` at the end of template body is for avoiding parsing the section node as plain text if there are some texts immediately after the template at the same line in some pages.

## Create Pydantic model

First we need to create [Pydantic](https://docs.pydantic.dev/latest/) models in file "models.py". Example file for Italian Wiktionary: [src/wiktextract/extractor/it/models.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/it/models.py)

Extractor code files are located in path "src/wiktextract/extractor", this guide use English Wiktionary as example, so we'll create file "src/wiktextract/extractor/en/models.py".

The closer the new model is to existing extractor models, the better. English Wiktionary extractor doesn't use Pydantic, it's JSON structure can be viewed at [here](https://kaikki.org/dictionary/errors/mapping/index.html). Non-en extractor JSON schema files generated from Pydantic models are at [here](https://tatuylonen.github.io/wiktextract/).

Pydantic model and fields should be added gradually with implementation code, directly copy all models from other extractors is not recommended.

```python
from pydantic import BaseModel, ConfigDict, Field

class EnglishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )

# word definition saved at here
class Sense(EnglishBaseModel):
    glosses: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []

# main JSON object
class WordEntry(EnglishBaseModel):
    model_config = ConfigDict(title="English Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = Field(
        default="", description="Original POS title"
    )
    senses: list[Sense] = Field(default=[], description="Sense list")
```

## Create "section_titles.py" file

This file contains POS and other section titles data. Example file from English Wiktionary extractor: [src/wiktextract/extractor/en/section_titles.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/en/section_titles.py)

```python
POS_DATA = {
    "Noun": {"pos": "noun"},
    "Verb": {"pos": "verb"},
}
```

## Create "page.py" file

All extractors start from the `parse_page()` function in file "page.py". Example file from Italian Wiktionary extractor: [src/wiktextract/extractor/it/page.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/it/page.py)

We could start implement the extractor to extract the definition lists, the example wikitext and JSON output are in the following "[Add test](#add-test)" section.

```python
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import POS_DATA

def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text in POS_DATA:
        wxr.wtp.start_subsection(title_text)
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)

    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # add page layout document link at here
    # https://en.wiktionary.org/wiki/Wiktionary:Entry_layout
    wxr.wtp.start_page(page_title)
    # `pre_expand` must be `True` if some section templates need to
    # be expanded before parsing:
    # root = wxr.wtp.parse(page_text, pre_expand=True)
    root = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level2_node in root.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        # language code can also be obtained from template name or parameter
        lang_code = name_to_code(lang_name, "en")
        base_data = WordEntry(
            word=page_title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        for next_level_node in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    return [m.model_dump(exclude_defaults=True) for m in page_data]
```

## Create "pos.py" file

Usually each section's code are in separate Python file. We'll create a new "pos.py" file to extract the POS section. Example file from Italian Wiktionary extractor: [src/wiktextract/extractor/it/pos.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/it/pos.py)

```python
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags

def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
):
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    for node in level_node.children:
        # Extract glosses: lists starting with "#" with senses for the words.
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LIST
            and node.sarg == "#"
        ):
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)

    # headword line templates like "head" should be handled here


def extract_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
):
    gloss_nodes = []
    sense = Sense()
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name in ["lb", "label"]:
            extract_lb_template(wxr, sense, node)
        else:
            gloss_nodes.append(node)
    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def extract_lb_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:label
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="label-content"
    ):
        sense.raw_tags.append(clean_node(wxr, None, span_tag))
    # save categories
    clean_node(wxr, sense, expanded_node)
```

There are three ways to extract a template:
- expand template, find data in expanded nodes: this method is used when data in only available when template is expanded or it's easier to extract data from node structure, for example, data may already separated in different nodes
- don't expand template, find data in template parameters: this is used when a template only display the parameter and does nothing more than that. If a template expand nodes contain category links, it's still need to be expanded to get the category data
- convert template node to text using `clean_node`: this is for expanded template text can be used directly or need minimal change

The first and second methods are sometimes used together when some data are easier to obtain from expanded nodes and some can be obtained directly from parameter without much change.

### Headword line form

Some editions use template to display forms data between POS section and gloss lists. For example, [ja-noun](https://en.wiktionary.org/wiki/Template:ja-noun) and [ru-noun+](https://en.wiktionary.org/wiki/Template:ru-noun+) in English Wiktionary. If the first bold word in expanded template has [`<ruby>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/ruby) annotations or in [stressed](https://en.wikipedia.org/wiki/Stress_(linguistics)) form and is different than the page title, a form data with "canonical" tag should be added. Example pages: [辞書](https://kaikki.org/dictionary/Japanese/meaning/辞/辞書/辞書.html), [словарь](https://kaikki.org/dictionary/Russian/meaning/с/сл/словарь.html)

## Create "tags.py" file

Tags are the English-language linguistics terms that should be common and shared between Wiktionary editions. For example, gender tags like "feminine" and "masculine", number tags like "singular" and "plural".

Tag data are added to the "raw_tags" field first, then we move tags that could be converted to tags to "tags" or "topics" field.

```python
from .models import WordEntry

TAGS = {
    "transitive": "transitive"
}
TOPICS = {
    "computing": "computing"
}

def translate_raw_tags(data: WordEntry):
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            data.tags.append(TAGS[raw_tag])
        elif raw_tag in TOPICS:
            data.topics.append(TOPICS[raw_tag])
    data.raw_tags = raw_tags
```

- English edition [sense tags](https://kaikki.org/dictionary/errors/mapping/index/senses/_list_/tags.html)
- English edition [form tags](https://kaikki.org/dictionary/errors/mapping/index/forms/_list_/tags.html)
- English edition [topics](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/topics.py)

## Add test

Create test file in "tests" folder. For example, [tests/test_it_gloss.py](https://github.com/tatuylonen/wiktextract/blob/master/tests/test_it_gloss.py). Tests should be included in the same git commit along with the extractor code, so it'll be more helpful for understanding the code when using git blame.

```python
from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestEnGloss(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )

    def tearDown(self):
        # remove temporary files
        self.wxr.wtp.close_db_conn()

    def test_gloss(self):
        self.wxr.wtp.add_page(
            "Template:lb",
            10,
            """{{#switch: {{{2}}}
| computing = <span class="usage-label-sense"><span class="ib-brac label-brac">(</span><span class="ib-content label-content">[[computing#Noun|computing]][[Category:en:Computing|DICTIONARY]]</span><span class="ib-brac label-brac">)</span></span>
| transitive = <span class="usage-label-sense"><span class="ib-brac label-brac">(</span><span class="ib-content label-content">[[Appendix:Glossary#transitive|transitive]][[Category:English transitive verbs|DICTIONARY]]</span><span class="ib-brac label-brac">)</span></span>
}}
""",
        )
        data = parse_page(
            self.wxr,
            "dictionary",
            """== English ==
===Noun===
# {{lb|en|computing}} An [[associative array]]

===Verb===
# {{lb|en|transitive}} To [[look up]] in a dictionary.""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "word": "dictionary",
                    "pos": "noun",
                    "pos_title": "Noun",
                    "senses": [
                        {
                            "glosses": ["An associative array"],
                            "categories": ["en:Computing"],
                            "topics": ["computing"]
                        }
                    ],
                },
                {
                    "lang": "English",
                    "lang_code": "en",
                    "word": "dictionary",
                    "pos": "verb",
                    "pos_title": "Verb",
                    "senses": [
                        {
                            "glosses": ["To look up in a dictionary."],
                            "categories": ["English transitive verbs"],
                            "tags": ["transitive"]
                        }
                    ],
                }
            ],
        )
```

`Wtp.add_page()` could be used to add templates required in test. If different expanded outputs are needed, we can use the [`#switch`](https://www.mediawiki.org/wiki/Help:Extension:ParserFunctions##switch) wikitext parser function to control the output.

Run `make test` command to check all tests, command `python -m unittest tests/test_en_*` only run en edition tests.

## Run `wiktwords` command

Command `wiktwords` can be used to test a single Wiktionary page or multiple pages if `--path` option is passed several times:

```
wiktwords --all --all-languages --edition en --db-path en_20250720.db --human --out page.json --page="dictionary" enwiktionary-20250720-pages-articles.xml.bz2
```

The "*.bz2" dump file path must be passed at the first use, it could be omitted at subsequent usages because page texts are saved to "en_20250720.db" file.

## Extract etymology section

POS sections could be under or at the same level of etymology section and pronunciation sections, we should be careful each section data are added to the right place according to the original wikitext section node structure.

### POS section and etymology section at the same level

```wikitext
== Language ==
=== Etymology ===
etymology text
=== POS 1 ===
# gloss
=== POS 2 ===
# gloss
```

In this layout, two `WordEntry` should be created for each POS section and they share the same etymology section data.

### POS section under etymology section

```wikitext
== Language ==
=== Etymology 1 ===
etymology 1
==== POS 1 ====
# gloss

=== Etymology 2 ===
etymology 2
==== POS 2 ====
# gloss
```

This layout also have two `WordEntry` for two POS sections but their etymology data are different.

Because etymology section is always above POS section(assume page layout rules are strictly enforced), we could extract etymology data to `base_data` and make a copy of `base_data` if etymology section has child section to handle both layout cases:

```python
import string

def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    title_text = title_text.rstrip(string.digits + string.whitespace)
    if title_text in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
    elif title_text == "Etymology":
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_etymology_section(wxr, base_data, level_node)

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    base_data.etymology_text = clean_node(
        wxr,
        base_data,
        list(level_node.invert_find_child(LEVEL_KIND_FLAGS)),
    )
```

Other sections around POS section may also have similar problem if an edition has messy inconsistent layout. For example, linkage section could be under POS section or at the same level of POS section:

```wikitext
=== POS 1 ===
# gloss
==== Synonyms ====
* [[word 1]]
=== POS 2 ===
# gloss
=== Antonyms ===
* [[word 2]]
```

"Antonyms" section data should be added to both `WordEntry`, while "Synonyms" section data should only be added to the first `WordEntry` for the first POS section. This can be done by checking the linkage section node type and `WordEntry.pos` and `WordEntry.lang_code` to make sure the data is added to the correct place:

```python
def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
):
    linkage_data = []
    if level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                getattr(data, linkage_type).extend(linkage_data)
    else:
        getattr(page_data[-1], linkage_type).extend(linkage_data)
```

## Extract nested gloss list

Some editions have nested gloss lists:

```wikitext
== English ==
=== Noun ===
# gloss 1
## gloss 2
```

Expected JSON output:

```json
{
    "senses": [
        {"glosses": ["gloss 1"]},
        {"glosses": ["gloss 1", "gloss 2"]}
    ]
}
```

We could modify `extract_gloss_list_item()` function to extract gloss lists recursively:

```python
def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
):
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "lb":
            extract_lb_template(wxr, sense, node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for e_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                # extract example or linkage data
                pass
        elif child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)
```

Don't forget to add a test after updating extractor code for a new wikitext layout or template.

## Extract example list

This example shows how to extract Japanese ruby data, add bold word offsets data, and how to handle example template under reference template layout.

Add test "tests/test_en_example.py":

```python
def test_ja_usex(self):
    self.wxr.wtp.add_page(
        "Template:quote-web",
        10,
        """<div class="citation-whole"><span class="cited-source">'''2020''' December 3, <span class="Jpan" lang="ja">中舘尚人</span>, “<span class="Jpan" lang="ja">災害対応と不確実性のマネジメント：第1回 “ウィズ不確実性”の時代</span>”, in <cite><span class="Jpan" lang="ja">[[:w&#58;ja&#58;経済産業研究所|経済産業研究所]]</span></cite> &#91;<cite><span class="e-translation">The Research Institute of Economy, Trade and Industry</span></cite>&#93;&lrm;<sup>[https://www.rieti.go.jp/jp/columns/a01_0621.html]</sup>:</span></div>"""
    )
    self.wxr.wtp.add_page(
        "Template:ja-usex",
        10,
        """<span lang="ja" class="Jpan"><span class="q-hellip-sp">&#32;</span><span class="q-hellip-b">[</span>…<span class="q-hellip-b">]</span><span class="q-hellip-b">&#32;</span>チリ<ruby>政府<rp>(</rp><rt>せいふ</rt><rp>)</rp></ruby>が<ruby>政治<rp>(</rp><rt>せいじ</rt><rp>)</rp></ruby>リスクを<ruby>犯<rp>(</rp><rt>おか</rt><rp>)</rp></ruby>して、<ruby>結果<rp>(</rp><rt>けっか</rt><rp>)</rp></ruby>を<ruby>約束<rp>(</rp><rt>やくそく</rt><rp>)</rp></ruby>したのは'''<ruby>大<rp>(</rp><rt>おお</rt><rp>)</rp></ruby>きい'''。</span><dl><dd><i><span class="tr"><Span class="q-hellip-sp">&#32;</span><span class="q-hellip-b">[</span>…<span class="q-hellip-b">]</span><span class="q-hellip-b">&#32;</span>chiri seifu ga seiji risuku o okashite, kekka o yakusoku shita no wa '''ōkii'''.</span></i></dd><dd>translation</dd></dl>[[Category:Japanese terms with usage examples|おおきい]][[Category:Japanese terms with usage examples|おおきい]]"""
    )
    data = parse_page(
        self.wxr,
        "大きい",
        """==Japanese==
===Adjective===
# [[important]]; [[crucial]]
#* {{quote-web|ja|date=2020-12-03|author=ja:中舘尚人|title=ja:災害対応と不確実性のマネジメント：第1回 “ウィズ不確実性”の時代|work=lw:ja:経済産業研究所|trans-work=The Research Institute of Economy, Trade and Industry|url=https://www.rieti.go.jp/jp/columns/a01_0621.html}}
#*: {{ja-usex|{{...}}チリ政府が政治リスクを犯して、結果を約束したのは'''大きい'''。|{{...}}チリ せいふ が せいじ リスク を おかして、けっか を やくそく した の は '''おおき.い'''。|translation}}"""
    )
    self.assertEqual(
        data[0]["senses"],
            [
                {
                    "categories": ["Japanese terms with usage examples"],
                    "examples": [
                        {
                            "bold_roman_offsets": [[73, 77]],
                            "bold_text_offsets": [[28, 31]],
                            "ref": "2020 December 3, 中舘尚人, “災害対応と不確実性のマネジメント：第1回 “ウィズ不確実性”の時代”, in 経済産業研究所 [The Research Institute of Economy, Trade and Industry]:",
                            "roman": "[…] chiri seifu ga seiji risuku o okashite, kekka o yakusoku shita no wa ōkii.",
                            "ruby": [
                                ["政府", "せいふ"],
                                ["政治", "せいじ"],
                                ["犯", "おか"],
                                ["結果", "けっか"],
                                ["約束", "やくそく"],
                                ["大", "おお"],
                            ],
                            "text": "[…] チリ政府が政治リスクを犯して、結果を約束したのは大きい。",
                            "translation": "translation",
                        }
                    ],
                    "glosses": ["important; crucial"],
                }
            ],
    )
```

Add Pydantic model:

```python
class Example(EnglishBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    roman: str = ""
    bold_roman_offsets: list[tuple[int, int]] = []
    ref = ""
    ruby: list[tuple[str, ...]] = []


class Sense(EnglishBaseModel):
    examples: list[Example] = []
```

Add "src/src/wiktextract/extractor/en/example.py":

```python
from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .models import Example, Sense, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
    word_entry: WordEntry,
    ref: str = "",
):
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name.startwith(
            "quote-"
        ):
            ref = extract_quote_template(wxr, sense, node)
        elif isinstance(node, TemplateNode) and node.template_name == "ja-usex":
            extract_ja_usex_template(wxr, sense, node, ref)
        # linkage template like "synonyms" will be extracted at here
        # elif isinstance(node, TemplateNode) and node.template_name in LINKAGE_TEMPLATES:
        #     pass
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(
                    wxr, sense, child_list_item, word_entry, ref
                )


def extract_quote_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> str:
    # https://en.wiktionary.org/wiki/Template:quote-book
    example = Example(text="")
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "cited-source" == span_class:
            example_data.ref = clean_node(wxr, None, span_tag)
        # other classes omitted
    clean_node(wxr, sense, expanded_node)
    if example.text != "":
        sense.examples.append(example)
    return example.ref


def extract_ja_usex_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode, ref: str
):
    # https://en.wiktionary.org/wiki/Template:ja-usex
    example = Example(text="", ref=ref)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="Jpan"
    ):
        ruby_data, node_without_ruby = extract_ruby(wxr, span_tag)
        example_data.text = clean_node(wxr, None, node_without_ruby)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(node_without_ruby)),
            example_data.text,
            example_data,
            "bold_text_offsets",
        )
        example_data.ruby = ruby_data
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example_data.roman = clean_node(wxr, None, span_tag)
        calculate_bold_offsets(
            wxr,
            span_tag,
            example_data.roman,
            example_data,
            "bold_roman_offsets",
        )
    tr_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get(3, "")),
        expand_all=True,
    )
    example_data.translation = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        tr_arg,
        example_data.translation,
        example_data,
        "bold_translation_offsets",
    )
    clean_node(wxr, sense, expanded_node)
    if example.text != "":
        sense.examples.append(example)
```

## Extract sound file

This example shows how to get sound file URLs.

First add test:

```python
def test_audio(self):
    self.wxr.wtp.add_page(
        "Template:audio",
        10,
        """<table class="audiotable"><tr><td>Audio <span class="ib-brac qualifier-brac">(</span><span class="usage-label-accent"><span class="ib-content label-content">[[w:Received Pronunciation|Received Pronunciation]]</span></span><span class="ib-brac qualifier-brac">)</span><span class="ib-colon qualifier-colon">:</span></td><td class="audiofile">[[File:En-uk-dictionary.ogg|noicon|175px]]</td><td class="audiometa" style="font-size: 80%;">([[:File:En-uk-dictionary.ogg|file]])</td></tr></table>[[Category:English terms with audio pronunciation|DICTIONARY]]"""
    )
    self.wxr.wtp.add_page(
        "Template:hyphenation",
        10,
        'Hyphenation: <span class="Latn" lang="en">dic‧tion‧a‧ry</span>, <span class="Latn" lang="en">dic‧tion‧ary</span>'
    )
    data = parse_page(
        self.wxr,
        "dictionary",
        """==English==
===Pronunciation===
* {{audio|en|En-uk-dictionary.ogg|a=RP}}
* {{hyphenation|en|dic|tion|a|ry||dic|tion|ary}}
===Noun===
# A [[reference work]]"""
    )
    self.assertEqual(
        data[0]["sounds"],
        [
            {
                "audio": "En-uk-dictionary.ogg",
                "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/1f/En-uk-dictionary.ogg/En-uk-dictionary.ogg.mp3",
                "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/1/1f/En-uk-dictionary.ogg",
                "tags": ["Received-Pronunciation"],
            }
        ]
    )
    self.assertEqual(
        data[0]["categories"], ["English terms with audio pronunciation"]
    )
    self.assertEqual(
        data[0]["hyphenations"],
        [
            {"parts": ["dic", "tion", "a", "ry"]},
            {"parts": ["dic", "tion", "ary"]},
        ],
    )
```

Add Pydantic model:

```python
class Sound(EnglishBaseModel):
    audio: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    tags: list[str] = []

class Hyphenation(EnglishBaseModel):
    parts: list[str] = []

class WordEntry(EnglishBaseModel):
    sounds: list[Sound] = []
    hyphenations: list[Hyphenation] = []
```

Wiktionary also use other audio file formats like WAV. This example only add `ogg_url` field for brevity.

Add "src/wiktextract/extractor/en/sound.py":

```python
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, word_entry, list_item)


def extract_sound_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
):
    for t_node in list_item.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "audio":
            extract_audio_template(wxr, word_entry, t_node)
        elif t_node.template_name == "hyphenation":
             extract_hyphenation_template(wxr, word_entry, t_node)


def extract_audio_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:audio
    sound = Sound()
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    set_sound_file_url_fields(wxr, filename, sound)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="label-content"
    ):
        raw_tag = clean_node(wxr, None, span_tag)
        if raw_tag != "":
            sound.raw_tags.append(raw_tag)
    translate_raw_tags(sound)
    word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, expanded_node)


def extract_hyphenation_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:hyphenation
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang
    ):
        h_str = clean_node(wxr, None, span_tag)
        h_data = Hyphenation(parts=h_str.split("‧"))
        word_entry.hyphenations.append(h_data)
```

Finally update `parse_section()` in file "page.py":

```python
from .sound import extract_sound_section

def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text == "Pronunciation":
        extract_sound_section(wxr, base_data, level_node)
```

## Extract translation section

First add test "tests/test_en_translation.py":

```python
def test_translation(self):
    self.wxr.wtp.add_page(
        "Template:tt+",
        10,
        '<span class="Arab" lang="ar">[[:قاموس#Arabic|قَامُوس]]</span><span class="tpos">&nbsp;[[:ar&#58;قاموس|(ar)]]</span>&nbsp;<span class="gender"><abbr title="masculine gender">m</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">qāmūs</span><span class="mention-gloss-paren annotation-paren">)</span>[[Category:Terms with Arabic translations|DICTIONARY]]'
    )
    self.wxr.wtp.add_page(
        "Template:tt",
        10,
        '<span class="Arab" lang="acw">[[:قاموس#Hijazi&#95;Arabic|قاموس]]</span>&nbsp;<span class="gender"><abbr title="masculine gender">m</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="acw-Latn" class="tr Latn">gāmūs</span><span class="mention-gloss-paren annotation-paren">)</span>[[Category:Terms with Hijazi Arabic translations|DICTIONARY]]'
    )
    data = parse_page(
        self.wxr,
        "dictionary",
        """==English==
===Noun===
# A [[reference work]]
====Translations====
{{multitrans|data=
{{trans-top|publication that explains the meanings of an ordered list of words}}
* Arabic: {{tt+|ar|قَامُوس|m}}
*: Hijazi Arabic: {{tt|acw|قاموس|m|tr=gāmūs}}
}}"""
    )
    self.assertEqual(
        data[0]["translations"],
        [
            {
                "lang_code": "ar",
                "lang": "Arabic",
                "word": "قَامُوس",
                "sense": "publication that explains the meanings of an ordered list of words",
                "roman": "qāmūs",
                "tags": ["masculine"],
            },
            {
                "lang_code": "acw",
                "lang": "Hijazi Arabic",
                "word": "قاموس",
                "sense": "publication that explains the meanings of an ordered list of words",
                "roman": "gāmūs",
                "tags": ["masculine"],
            },
        ]
    )
```

Then create Pydantic model:

```python
class Translation(EnglishBaseModel):
    lang_code: str = ""
    lang: str = ""
    word: str = ""
    sense: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""


class WordEntry(EnglishBaseModel):
    translations: list[Translation] = []
```

Implement extractor code "src/wiktextract/extractor/en/translation.py":

```python
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    sense = ""
    for node in level_node.children:
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "multitrans"
        ):
            extract_multitrans_template(wxr, word_entry, node)
        elif (
            isinstance(node, TemplateNode) and node.template_name == "trans-top"
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(wxr, word_entry, node, sense)


def extract_multitrans_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:multitrans
    data_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node.template_parameters.get("data", ""))
    )
    extract_translation_section(wxr, word_entry, data_arg)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
):
    lang_name = "unknown"
    if node in list_item.children:
        if (
            isinstance(node, str)
            and node.strip().endswith(":")
            and lang_name == "unknown"
        ):
            lang_name = node.strip(": ")
        elif isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "tt+",
            "tt",
        ]:
            extract_t_template(wxr, word_entry, node, lang_name, sense)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense
                )


def extract_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    lang_name: str,
    sense: str,
):
    # https://en.wiktionary.org/wiki/Template:t
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    t_data = Translation(lang=lang_name, lang_code=lang_code, sense=sense)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "")
        if span_lang == lang_code:
            t_data.word = clean_node(wxr, None, span_tag)
        elif span_lang == f"{lang_code}-Latn":
            t_data.roman = clean_node(wxr, None, span_tag)
        elif span_class == "gender":
            for abbr_tag in span_tag.find_html("abbr"):
                raw_tag = clean_node(wxr, None, abbr_tag)
                if raw_tag != "":
                    t_data.raw_tags.append(raw_tag)
    if t_data.word != "":
        translate_raw_tags(t_data)
        word_entry.translations.append(t_data)
```

Finally update `parse_section()`:

```python
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text == "Translations":
        extract_translation_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node
        )
```

### Translation subpage

Some pages have [translation subpage](https://en.wiktionary.org/wiki/Category:Translation_subpages), for example: [book/translations](https://en.wiktionary.org/wiki/book/translations). These pages should be skipped in `parse_page()`:

```python
def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    if page_title.endswith("/translations"):
        return []
```

We could use `Wtp.get_page()` to get subpage wikitext:

```python
def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for node in level_node.children:
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "see translation subpage"
        ):
            extract_subpage_template(wxr, word_entry, node)


def extract_subpage_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:see_translation_subpage
    pos = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    second_arg = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    subpage_title = wxr.wtp.title + "/translations"
    if second_arg != "":
        subpage_title = second_arg
    subpage = wxr.wtp.get_page(subpage_title, namespace_id=0)
    if subpage is None:
        return
    root = wxr.wtp.parse(subpage.body)
    if pos != "":
        pos_section = get_subpage_section(wxr, root, pos)
        if pos_section is None:
            return
        tr_section = get_subpage_section(wxr, pos_section, "Translations")
    else:
        tr_section = get_subpage_section(wxr, root, "Translations")
    if tr_section is not None:
        extract_translation_section(wxr, word_entry, tr_section)


def get_subpage_section(
    wxr: WiktextractContext, node: WikiNode, target_section: str
) -> LevelNode | None:
    for level_node in node.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title == target_section:
            return level_node
```

## Extract linkage sections

Linkage sections contain data like synonym and antonym words. These data are saved to "synonyms" and "antonyms" fields. English Wiktionary linkage fields are in the `LINKAGE_TITLES` dictionary in file [src/wiktextract/extractor/en/section_titles.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/en/section_titles.py).

First add test:

```python
def test_linkage(self):
    self.wxr.wtp.add_page(
        "Template:l",
        10,
        """<span class="Latn" lang="en">[[{{{2}}}]]</span>"""
    )
    self.wxr.wtp.add_page(
        "Template:col3",
        10,
        """<div class="list-switcher-wrapper"><div class="list-switcher-header">Hyponyms of ''engine''</div><div class="term-list columns-bg"><ul><li><span class="Latn" lang="en">[[:aero engine#English|aero engine]]</span></li><li><span class="Latn" lang="en">[[:air engine#English|air engine]]</span></li></ul></div></div>"""
    )
    data = parse_page(
        self.wxr,
        "engine",
        """==English==
===Noun===
# A large [[construction]] used in [[warfare]]

====Synonyms====
* {{l|en|motor}}
* {{l|en|locomotive}}

====Hyponyms====
{{col3|en|title= Hyponyms of ''engine''
|aero engine
|air engine
}}"""
    )
    self.assertEqual(
        data[0]["synonyms"], [{"word": "motor"}, {"word": "locomotive"}]
    )
    self.assertEqual(
        data[0]["hyponyms"], [{"word": "aero engine"}, {"word": "air engine"}]
    )
```

Add linkage Pydantic model:

```python
class Linkage(EnglishBaseModel):
    word: str = ""

class WordEntry(EnglishBaseModel):
    synonyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
```

Add linkage section titles to "section_titles.py":

```python
LINKAGE_TITLES = {
    "Synonyms": "synonyms",
    "Hyponyms": "hyponyms",
}
```

Add section extractor code "src/wiktextract/extractor/en/linkages.py":

```python
import re
from .models import Linkage, WordEntry


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
):
    linkage_list = []
    for node in level_node.children:
        if isinstance(node, TemplateNode) and re.fullmatch(r"col\d", node.template_name):
            linkage_list.extend(extract_col_template(wxr, node))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                linkage_list.extend(extract_linkage_list_item(wxr, list_item))

    getattr(word_entry, linkage_type).extend(linkage_list)


def extract_linkage_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Linkage]:
    l_list = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "l":
            l_list.extend(extract_l_template(wxr, node))

    return l_list


def extract_l_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Linkage]:
    # https://en.wiktionary.org/wiki/Template:link
    l_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang
    ):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            l_list.append(Linkage(word=word))
    return l_list


def extract_col_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Linkage]:
    # https://en.wiktionary.org/wiki/Template:col
    l_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for li_tag in expanded_template.find_html_recursively("li"):
        for span_tag in li_tag.find_html(
            "span", attr_name="lang", attr_value=lang
        ):
            word = clean_node(wxr, None, span_tag)
            if word != "":
                l_list.append(Linkage(word=word))
    return l_list
```

In this example, the linkage word could be extracted directly from template parameters. But in practice, we still need to find data in expanded node because gender tag, romanization and Traditional/Simplified Chinese data are only available in expanded nodes. Also some templates like [syn-saurus](https://en.wiktionary.org/wiki/Template:syn-saurus) and [zh-dial](https://en.wiktionary.org/wiki/Template:zh-dial), template parameter may not exist or useless and must be expanded.

Finally update `parse_section()`:

```python
from .linkage import extract_linkage_section
from .section_titles import LINKAGE_TITLES


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text in LINKAGE_TITLES:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_TITLES[title_text]
        )
```

## Extract conjugation table template

Most editions have conjugation templates expand to wikitext table, HTML table or mix of wikitext and HTML tags. Some table templates don't use the correct wikitext or HTML tags, like using table cell wikitext(`|`) for header cell(`!`) or use `<td>` HTML tag for table header(should use `<th>`), these mistakes should be fixed on Wiktionary.

First add test "tests/test_en_forms.py":

```python
    def test_sv_conj_wk(self):
        self.wxr.wtp.add_page(
            "Template:sv-conj-wk",
            10,
            """<div>
{| class="inflection-table  "
|+ class="inflection-table-title" | Conjugation of <i class="Latn mention" lang="sv">läsa</i> (weak)
|-
! class="outer" |
! colspan=2 class="outer" | active
! colspan=2 class="outer" | passive
|-
! infinitive
| colspan=2 | <span class="Latn" lang="sv">[[:läsa#Swedish|läsa]]</span>
| colspan=2 | <span class="Latn" lang="sv">[[:läsas#Swedish|läsas]]</span>
|}
</div>[[Category:Swedish weak verbs|LÄSA]]"""
        )
        data = parse_page(
            self.wxr,
            "läsa",
            """==Swedish==
===Verb===
# to [[read]] (text)
====Conjugation====
{{sv-conj-wk|läs|end=s}}"""
        )
        self.assertEqual(
            data[0]["forms"],
            [{"form": "läsas", "tags": ["infinitive", "passive"]}],
        )
        self.assertEqual(
            data[0]["categories"], ["Swedish weak verbs"]
        )
```

Add `Form` pydantic model to "src/wiktextract/extractor/en/models.py":

```python
class Form(EnglishBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []

class WordEntry(EnglishBaseModel):
    forms: list[Form] = []
```

Implement table template extractor "src/wiktextract/extractor/en/conjugation.py":

```python
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_conjugation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "sv-conj-wk":
            extract_sv_conj_wk_template(wxr, word_entry, t_node)


def extract_sv_conj_wk_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:sv-conj-wk
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child_recursively(NodeKind.TABLE):
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            col_index = 0
            is_header_row = not row.contain_node(NodeKind.TABLE_CELL)
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if is_header_row:
                        col_header = clean_node(wxr, None, cell)
                        if col_header != "":
                            col_headers.append(col_header)
                    else:
                        row_header = clean_node(wxr, None, cell)
                else:
                    word = clean_node(wxr, None, cell)
                    if word not in ["", wxr.wtp.title]:
                        form = Form(form=word)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if col_index < len(col_headers):
                            form.raw_tags.append(col_headers[col_index])
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                    col_index += 1

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)
```

Finally update `parse_section()` in "page.py":

```python
from .conjugation import extract_conjugation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text == "Conjugation":
        extract_conjugation_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
        )
```
