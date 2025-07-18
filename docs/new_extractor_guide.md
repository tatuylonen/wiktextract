# Create new Wiktionary extractor guide

## Learn wikitext

Read [this document](https://en.wikipedia.org/wiki/Help:Wikitext) to learn the basic syntax of wikitext.

## Read Wiktionary entry layout document

Every Wiktionary has their unique page layout, they usually have a document page of the layout and other rules. For example, here is English Wiktionary's document: [Wiktionary:Entry layout](https://en.wiktionary.org/wiki/Wiktionary:Entry_layout). After reading the layout document, try edit some pages.

## Choose which namespaces to use from dump file

MediWiki pages are grouped in collections called "[namespaces](https://www.mediawiki.org/wiki/Help:Namespaces)". By default, "Main", "Template", "Module" namespaces are used, their corresponding ids are `0`, `10`, `828`. "Main" namespace contains word pages, "Module" namespace contain Lua code used in templates. If pages in other namespaces are needed, they should be added in a `config.json` file. For example, [here](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/data/fr/config.json) is the JSON file for French Wiktionary. All namespace names and ids can be found at the start of [dump file](https://dumps.wikimedia.org/backup-index.html)("*-pages-articles.xml.bz2" file). You may need to update the [namespace data file](https://github.com/tatuylonen/wikitextprocessor/tree/main/src/wikitextprocessor/data) in wikitextprocessor package, these files should be updated using this [script](https://github.com/tatuylonen/wikitextprocessor/blob/main/tools/get_namespaces.py).

## Pre-expand section templates

Some Wiktionary editions use templates to expand to section wikitext or HTML tags, these templates need to be expanded before parsing the page to nodes. Skip this step if the new Wiktionary doesn't have this problem.

### Section template expands to wikitext

Write a `analyze_template()` in file "analyze_template.py", this function checks all template pages and return `True` if the template need pre-expand. Example [file](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/nl/analyze_template.py) of Dutch Wiktionary.

### Section template expands to HTML

Templates can be overridden to expand to wikitext. Example [override file](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/data/overrides/id.json) for Indonesian Wiktionary. The new line character `\n` at the end of template body is for avoiding parsing text directly after the template as part of section node.

## Create Pydantic model

New extractor usually start from extracting definition lists. First we need to create [Pydantic](https://docs.pydantic.dev/latest/) model in file "models.py". Example file for Italian Wiktionary: [src/wiktextract/extractor/it/models.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/it/models.py)

The closer the new model is to existing extractor models, the better. English Wiktionary extractor doesn't use Pydantic, it's JSON structure can be viewed at [here](https://kaikki.org/dictionary/errors/mapping/index.html).

```python
from pydantic import BaseModel, ConfigDict, Field

class EnglishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )

class Sense(EnglishBaseModel):
    glosses: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []

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

## Learn wikitextprocessor parser API

Here is a simplified wikitext of English Wiktionary page [dictionary](https://en.wiktionary.org/wiki/dictionary)

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
    """== English ==
===Noun===
# {{lb|en|computing}} An [[associative array]]"""
)
```

The level 3 POS node is the child of level 2 language node.

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
root.children
# [<LEVEL2(['English']){} '\n', <LEVEL3(['Noun']){} '\n', <LIST(#){} <LIST_ITEM(#){} ' ', <TEMPLATE(['lb'], ['en'], ['computing']){} >, ' An ', <LINK(['associative array']){} >>>>>]
```

Child node can be located with these APIs: `WikiNode.find_child()`, `WikiNode.find_child_recursively()`, `WikiNode.invert_find_child()`, `WikiNode.find_html()`, `WikiNode.find_html_recursively()`. Parser API source code: [src/wikitextprocessor/parser.py](https://github.com/tatuylonen/wikitextprocessor/blob/main/src/wikitextprocessor/parser.py)

```python
from wikitextprocessor import NodeKind

for t_node in root.find_child_recursively(NodeKind.TEMPLATE):
    pass
```

Template can be expanded like this:

```python
expanded_node = wxr.wtp.parse(
    wxr.wtp.node_to_wikitext(t_node), expand_all=True
)
```

MediaWiki's special page [Special:ExpandTemplates](https://en.wiktionary.org/wiki/Special:ExpandTemplates) can be used to obtain the expanded wikitext of a template, this is very helpful when writing extractor for template.

`clean_node()` can be used to convert node to text:

```python
from wiktextract.page import clean_node

clean_node(wxr, None, t_node)
# "(computing)"
```

The second argument of `clean_node()` is for saving [category links](https://en.wikipedia.org/wiki/Help:Wikitext#Categories), it can be dictionary or pydantic model or `None`. If it's not `None`, a list of strings will be added to the "categories" field of pydantic model or dictionary.

Template name and parameters are available as properties of `TemplateNode` class:

```python
t_node.template_name
# "lb"
t_node.template_parameters
# {1: 'en', 2: 'computing'}
```

The `TemplateNode.template_parameters` dictionary values can't be used directly. If you want to find a node in a template parameter, the value must be parsed:

```python
parsed_arg = wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value))
```

If text string is needed, `clean_node()` should be used:

```python
clean_node(wxr, None, t_node.template_parameters[1])
```

`LevelNode.find_content()` is used to find node inside the level node but not the child nodes:

```python
root = wxr.wtp.parse("=={{lang|en}}==\ntext")
for t_node in root.find_content(NodeKind.TEMPLATE):
    pass
```

Nodes inside level node wikitext are in `LevelNode.largs` list:

```python
root = wxr.wtp.parse("==English==\ntext")
for level_node in root.find_child(NodeKind.LEVEL2):
    print(clean_node(wxr, None, level_node.largs))
    # "English"
```

For description lists, term nodes are in the `WikiNode.children` attribute, definition nodes are in the `WikiNode.definition` attribute:

```python
root = wxr.wtp.parse("; term : definition")
list_item = next(root.find_child_recursively(NodeKind.LIST_ITEM))
list_item.children
# [' term ']
list_item.definition
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

## Create "page.py" file

All extractors start from the `parse_page()` function in file "page.py". Example file from Italian Wiktionary extractor: [src/wiktextract/extractor/it/page.py](https://github.com/tatuylonen/wiktextract/blob/master/src/wiktextract/extractor/it/page.py)

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
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text in POS_DATA:
        wxr.wtp.start_subsection(title_text)
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)

    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://en.wiktionary.org/wiki/Wiktionary:Entry_layout
    wxr.wtp.start_page(page_title)
    # `pre_expand` must be `True` if some section templates need to
    # be expanded before parsing
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        # language code can also be obtained from template name or parameter
        lang_code = name_to_code(lang_name, "en")
        base_data = WordEntry(
            word=wxr.wtp.title,
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
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    for node in level_node.children:
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LIST
            and node.sarg.startswith("#")
            and node.sarg.endswith("#")
        ):
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)


def extract_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    gloss_nodes = []
    sense = Sense()
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "lb":
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
) -> None:
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

## Create "tags.py" file

Tags data are added to the "raw_tags" field first, then we move tags that could be converted to tags used in English Wiktionary to "tags" or "topics" field.

```python
from .models import WordEntry

TAGS = {
    "transitive": "transitive"
}
TOPICS = {
    "computing": "computing"
}

def translate_raw_tags(data: WordEntry) -> None:
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

Create test file in "tests" folder. For example, [tests/test_it_gloss.py](https://github.com/tatuylonen/wiktextract/blob/master/tests/test_it_gloss.py)

```python
from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestEnGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )

    def tearDown(self):
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
