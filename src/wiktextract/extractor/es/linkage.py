from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .section_titles import LINKAGE_TITLES


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
):
    linkage_list = []
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        sense_nodes = []
        after_colon = False
        words = []
        for node in list_item_node.children:
            if after_colon:
                sense_nodes.append(node)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                words.append(clean_node(wxr, None, node))
            elif isinstance(node, TemplateNode) and node.template_name == "l":
                words.append(clean_node(wxr, None, node))
            elif isinstance(node, str) and ":" in node:
                after_colon = True
                sense_nodes.append(node[node.index(":") + 1 :])
        sense = clean_node(wxr, None, sense_nodes)
        for word in filter(None, words):
            linkage_list.append(Linkage(word=word, sense=sense))

    for data in page_data:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.etymology_text == page_data[-1].etymology_text
        ):
            getattr(data, linkage_type).extend(linkage_list)


def process_linkage_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://es.wiktionary.org/wiki/Plantilla:sinónimo
    linkage_type = LINKAGE_TITLES.get(t_node.template_name.removesuffix("s"))
    for index in range(1, 41):
        if index not in t_node.template_parameters:
            break
        linkage_data = Linkage(
            word=clean_node(wxr, None, t_node.template_parameters[index])
        )
        if len(word_entry.senses) > 0:
            linkage_data.sense_index = word_entry.senses[-1].sense_index
            linkage_data.sense = " ".join(word_entry.senses[-1].glosses)
        getattr(word_entry, linkage_type).append(linkage_data)
        process_linkage_template_parameter(
            wxr, linkage_data, t_node, f"nota{index}"
        )
        process_linkage_template_parameter(
            wxr, linkage_data, t_node, f"alt{index}"
        )
        if index == 1:
            process_linkage_template_parameter(
                wxr, linkage_data, t_node, "nota"
            )
            process_linkage_template_parameter(wxr, linkage_data, t_node, "alt")


def process_linkage_template_parameter(
    wxr: WiktextractContext,
    linkage_data: Linkage,
    template_node: TemplateNode,
    param: str,
) -> None:
    if param in template_node.template_parameters:
        value = clean_node(wxr, None, template_node.template_parameters[param])
        if param.startswith("nota"):
            linkage_data.note = value
        elif param.startswith("alt"):
            linkage_data.alternative_spelling = value


def extract_alt_form_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    has_link = False
    for link_node in level_node.find_child(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        has_link = True
        if word != "":
            word_entry.forms.append(Form(form=word, tags=["alt-of"]))
    if not has_link:
        section_text = clean_node(
            wxr,
            None,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
        ).removesuffix(".")
        for word in section_text.split(","):
            word = word.strip()
            if word != "":
                word_entry.forms.append(Form(form=word, tags=["alt-of"]))


def extract_additional_information_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "cognados",
            "derivad",
            "morfología",
        ]:
            extract_cognados_template(wxr, word_entry, node)


def extract_cognados_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:cognados
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    l_list = []
    for span_tag in expanded_node.find_html_recursively("span"):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            l_list.append(Linkage(word=word))

    if t_node.template_name == "cognados":
        word_entry.cognates.extend(l_list)
    elif t_node.template_name == "derivad":
        word_entry.derived.extend(l_list)
    elif t_node.template_name == "morfología":
        word_entry.morphologies.extend(l_list)
