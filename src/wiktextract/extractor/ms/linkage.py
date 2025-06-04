from collections import defaultdict

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS


def extract_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
        if (
            isinstance(node, TemplateNode)
            and node.template_name in ["ARchar", "Arab", "PSchar", "SDchar"]
        ) or node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.forms.append(Form(form=word, tags=tags))
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.find_child(NodeKind.LINK):
                word = clean_node(wxr, None, node)
                if word != "":
                    word_entry.forms.append(Form(form=word, tags=tags))


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    l_dict = defaultdict(list)
    linkage_name = clean_node(wxr, None, level_node.largs).lower()
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            new_l_name = extract_linkage_list_item(
                wxr, l_dict, linkage_name, list_item
            )
            if new_l_name != "":
                linkage_name = new_l_name

    if len(page_data) == 0 or page_data[-1].lang_code != base_data.lang_code:
        for field, data in l_dict.items():
            getattr(base_data, field).extend(data)
    elif level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                for field, l_data in l_dict.items():
                    getattr(data, field).extend(l_data)
    else:
        for field, l_data in l_dict.items():
            getattr(page_data[-1], field).extend(l_data)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    l_dict: dict[str, list[Linkage]],
    linkage_name: str,
    list_item: WikiNode,
) -> str:
    if list_item.definition is not None and len(list_item.definition) > 0:
        linkage_name = clean_node(wxr, None, list_item.children).lower()
        if linkage_name not in LINKAGE_SECTIONS:
            return ""
        for node in list_item.definition:
            if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                if word != "":
                    l_dict[LINKAGE_SECTIONS[linkage_name]].append(
                        Linkage(word=word)
                    )
            elif isinstance(node, str):
                for word in node.split(","):
                    word = word.strip(" .\n")
                    if word != "":
                        l_dict[LINKAGE_SECTIONS[linkage_name]].append(
                            Linkage(word=word)
                        )
    else:
        sense = ""
        for node in list_item.children:
            if isinstance(node, TemplateNode) and node.template_name == "sense":
                sense = clean_node(wxr, None, node).strip("(): ")
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                if word != "" and linkage_name in LINKAGE_SECTIONS:
                    l_dict[LINKAGE_SECTIONS[linkage_name]].append(
                        Linkage(word=word, sense=sense)
                    )
            elif isinstance(node, str) and node.strip().endswith(":"):
                new_linkage_name = node.strip("(): ").lower()
                if new_linkage_name in LINKAGE_SECTIONS:
                    linkage_name = new_linkage_name

    return linkage_name


LINKAGE_TEMPLATES = {
    "antonim": "antonyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
    "sinonim": "synonyms",
    "synonyms": "synonyms",
    "syn": "synonyms",
    "sin": "synonyms",
    "hypernyms": "hypernyms",
    "hyper": "hypernyms",
    "kata setara": "coordinate_terms",
    "coordinate terms": "coordinate_terms",
    "perkataan koordinat": "coordinate_terms",
    "cot": "coordinate_terms",
    "hiponim": "hyponyms",
    "hipo": "hyponyms",
    "hyponyms": "hyponyms",
}


def extract_nyms_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # Modul:nyms
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html_recursively("span"):
        if lang_code == span_tag.attrs.get("lang", ""):
            word = clean_node(wxr, None, span_tag)
            if word != "":
                l_data = Linkage(word=word)
                if (
                    len(word_entry.senses) > 0
                    and len(word_entry.senses[-1].glosses) > 0
                ):
                    l_data.sense = " ".join(word_entry.senses[-1].glosses)
                getattr(
                    word_entry, LINKAGE_TEMPLATES[t_node.template_name]
                ).append(l_data)
