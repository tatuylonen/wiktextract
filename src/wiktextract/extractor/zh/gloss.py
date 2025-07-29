import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .example import extract_example_list_item
from .models import AltForm, Classifier, Sense, WordEntry
from .tags import translate_raw_tags

# https://zh.wiktionary.org/wiki/Template:Label
LABEL_TEMPLATES = frozenset(["lb", "lbl", "label"])

# https://zh.wiktionary.org/wiki/Category:/Category:之形式模板
FORM_OF_TEMPLATES = frozenset(
    [
        "alt case",
        "alt formaltform",
        "alt sp",
        "construed with",
        "honor alt case",
        "missp",
        "obs sp",
        "rare sp",
        "rfform",
        "short for",
        "stand sp",
        "sup sp",
    ]
)
ABBR_TEMPALTES = frozenset(
    [
        "之縮寫",
        "abbreviation of",
        "abbr of",
        "abbrev of",
        "zh-short",
        "zh-abbrev",
        "中文简称",
    ]
)
ZH_ALT_OF_TEMPLATES = frozenset(
    ["zh-altname", "zh-alt-name", "中文別名", "中文别名"]
)


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    parent_gloss_data: Sense,
) -> None:
    lang_code = page_data[-1].lang_code
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = []
        raw_tags = []
        gloss_data = parent_gloss_data.model_copy(deep=True)
        for node in list_item_node.children:
            if isinstance(node, TemplateNode):
                if node.template_name == "rfdef":
                    continue
                raw_tag = clean_node(wxr, gloss_data, node)
                if node.template_name.lower() in LABEL_TEMPLATES:
                    for r_tag in re.split(r"，|或", raw_tag.strip("()")):
                        r_tag = r_tag.strip()
                        if r_tag != "":
                            raw_tags.append(r_tag)
                elif raw_tag.startswith("〈") and raw_tag.endswith("〉"):
                    raw_tags.append(raw_tag.strip("〈〉"))
                elif (
                    node.template_name
                    in FORM_OF_TEMPLATES | ABBR_TEMPALTES | ZH_ALT_OF_TEMPLATES
                    or node.template_name.endswith((" of", " form", "-form"))
                ) and process_form_of_template(
                    wxr, node, gloss_data, page_data
                ):
                    pass
                elif node.template_name == "zh-mw":
                    process_zh_mw_template(wxr, node, gloss_data)
                elif node.template_name.lower() in ["zh-obsolete", "†", "zh-o"]:
                    if "obsolete" not in gloss_data.tags:
                        gloss_data.tags.append("obsolete")
                else:
                    gloss_nodes.append(node)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                continue
            else:
                gloss_nodes.append(node)

        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            gloss_text = clean_node(wxr, gloss_data, nodes_without_ruby)
        else:
            ruby_data = []
            gloss_text = clean_node(wxr, gloss_data, gloss_nodes)

        gloss_data.raw_tags.extend(raw_tags)
        if len(gloss_text) > 0:
            gloss_data.glosses.append(gloss_text)
        if len(ruby_data) > 0:
            gloss_data.ruby = ruby_data

        has_nested_gloss = False
        if list_item_node.contain_node(NodeKind.LIST):
            for next_list in list_item_node.find_child(NodeKind.LIST):
                if next_list.sarg.endswith("#"):  # nested gloss
                    has_nested_gloss = True
                    extract_gloss(wxr, page_data, next_list, gloss_data)
                else:
                    for e_list_item in next_list.find_child(NodeKind.LIST_ITEM):
                        extract_example_list_item(
                            wxr, gloss_data, e_list_item, page_data[-1]
                        )

        if not has_nested_gloss and len(gloss_data.glosses) > 0:
            translate_raw_tags(gloss_data)
            page_data[-1].senses.append(gloss_data)


def process_form_of_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: Sense,
    page_data: list[WordEntry],
) -> bool:
    # Return `True` if template expands to list or don't want add gloss again
    # in `extract_gloss()`
    # https://en.wiktionary.org/wiki/Category:Form-of_templates
    # https://en.wiktionary.org/wiki/Category:Form-of_templates_by_language
    is_alt_of = (
        re.search(r"^alt|alt[\s-]|alternative", t_node.template_name.lower())
        or t_node.template_name.lower() in ZH_ALT_OF_TEMPLATES
    )
    is_abbr = t_node.template_name.lower() in ABBR_TEMPALTES
    if is_alt_of:
        sense.tags.append("alt-of")
    elif is_abbr:
        sense.tags.extend(["alt-of", "abbreviation"])
    else:
        sense.tags.append("form-of")
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    if t_node.template_name.endswith("-erhua form of"):
        process_erhua_form_of_template(wxr, expanded_template, sense)
        return True
    elif (
        t_node.template_name.lower()
        in {"zh-short", "zh-abbrev", "中文简称"} | ZH_ALT_OF_TEMPLATES
    ):
        extract_zh_abbr_template(wxr, expanded_template, sense)
        return False

    form_of_words = []
    for i_tag in expanded_template.find_html_recursively("i"):
        form_of_words = process_form_of_template_child(wxr, i_tag)

    if len(form_of_words) == 0:
        for link_node in expanded_template.find_child_recursively(
            NodeKind.LINK
        ):
            form_of_words = process_form_of_template_child(wxr, link_node)
            break
    for form_of_word in form_of_words:
        form_of = AltForm(word=form_of_word)
        if is_alt_of or is_abbr:
            sense.alt_of.append(form_of)
        else:
            sense.form_of.append(form_of)

    if expanded_template.contain_node(NodeKind.LIST):
        shared_gloss = clean_node(
            wxr, None, list(expanded_template.invert_find_child(NodeKind.LIST))
        )
        for list_item_node in expanded_template.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            new_sense = sense.model_copy(deep=True)
            new_sense.glosses.append(shared_gloss)
            new_sense.glosses.append(
                clean_node(wxr, None, list_item_node.children)
            )
            page_data[-1].senses.append(new_sense)
        return True

    return False


def process_form_of_template_child(
    wxr: WiktextractContext, node: WikiNode
) -> list[str]:
    form_of_words = []
    span_text = clean_node(wxr, None, node)
    for form_of_word in span_text.split("和"):
        form_of_word = form_of_word.strip()
        if form_of_word != "":
            form_of_words.append(form_of_word)
    return form_of_words


def process_erhua_form_of_template(
    wxr: WiktextractContext, expanded_node: WikiNode, sense: Sense
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Cmn-erhua_form_of
    for index, span_node in enumerate(
        expanded_node.find_html("span", attr_name="lang", attr_value="zh")
    ):
        span_text = clean_node(wxr, None, span_node)
        form = AltForm(word=span_text)
        if index == 0:
            form.tags.append("Traditional-Chinese")
        else:
            form.tags.append("Simplified-Chinese")
        if len(form.word) > 0:
            sense.form_of.append(form)
    gloss_text = clean_node(wxr, sense, expanded_node)
    if gloss_text.startswith("(官話)"):
        gloss_text = gloss_text.removeprefix("(官話)").strip()
        sense.tags.append("Mandarin")
    sense.tags.append("Erhua")
    if len(gloss_text) > 0:
        sense.glosses.append(gloss_text)


def process_zh_mw_template(
    wxr: WiktextractContext, node: TemplateNode, sense: Sense
) -> None:
    # Chinese inline classifier template
    # https://zh.wiktionary.org/wiki/Template:分類詞
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    classifiers = []
    last_word = ""
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if span_class in ["Hani", "Hant", "Hans"]:
            word = clean_node(wxr, None, span_tag)
            if word != "／":
                classifier = Classifier(classifier=word)
                if span_class == "Hant":
                    classifier.tags.append("Traditional-Chinese")
                elif span_class == "Hans":
                    classifier.tags.append("Simplified-Chinese")

                if len(classifiers) > 0 and last_word != "／":
                    sense.classifiers.extend(classifiers)
                    classifiers.clear()
                classifiers.append(classifier)
            last_word = word
        elif "title" in span_tag.attrs:
            raw_tag = clean_node(wxr, None, span_tag.attrs["title"])
            if len(raw_tag) > 0:
                for classifier in classifiers:
                    classifier.raw_tags.append(raw_tag)
    sense.classifiers.extend(classifiers)
    for classifier in sense.classifiers:
        translate_raw_tags(classifier)


def extract_zh_abbr_template(
    wxr: WiktextractContext, expanded_node: WikiNode, sense: Sense
):
    # https://zh.wiktionary.org/wiki/Template:Zh-short
    roman = ""
    for i_tag in expanded_node.find_html("i"):
        roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html("span"):
        span_class = span_tag.attrs.get("class", "")
        alt_form = AltForm(word=clean_node(wxr, None, span_tag), roman=roman)
        if span_class == "Hant":
            alt_form.tags.append("Traditional-Chinese")
        elif span_class == "Hans":
            alt_form.tags.append("Simplified-Chinese")
        if alt_form.word not in ["", "／"]:
            sense.alt_of.append(alt_form)
