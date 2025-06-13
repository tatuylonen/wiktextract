from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    l_type: str,
    tags: list[str],
) -> None:
    sense = ""
    l_list = []
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name.lower() in [
            "üst",
            "trans-top",
        ]:
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_node in level_node.find_child(NodeKind.LIST):
                for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                    l_list.extend(
                        extract_linkage_list_item(
                            wxr, word_entry, list_item, tags, sense
                        )
                    )
    for link_node in level_node.find_child(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if word != "":
            l_list.append(Linkage(word=word, tags=tags))

    if l_type == "forms":
        for l_data in l_list:
            word_entry.forms.append(
                Form(
                    form=l_data.word,
                    tags=l_data.tags,
                    raw_tags=l_data.raw_tags,
                    roman=l_data.roman,
                )
            )
    else:
        getattr(word_entry, l_type).extend(l_list)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    tags: list[str],
    sense: str,
) -> list[Linkage]:
    l_list = []
    for node in list_item.children:
        if (isinstance(node, WikiNode) and node.kind == NodeKind.LINK) or (
            isinstance(node, TemplateNode)
            and node.template_name in ["bağlantı", "l", "b"]
        ):
            l_data = Linkage(
                word=clean_node(wxr, None, node), sense=sense, tags=tags
            )
            if l_data.word != "":
                l_list.append(l_data)
        elif isinstance(node, TemplateNode):
            if node.template_name in ["anlam", "mânâ", "mana"]:
                sense = clean_node(wxr, None, node).strip("(): ")
            elif node.template_name == "şerh" and len(l_list) > 0:
                raw_tag = clean_node(wxr, None, node).strip("() ")
                if raw_tag != "":
                    l_list[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(l_list[-1])
    return l_list


GLOSS_LIST_LINKAGE_TEMPLATES = {
    "eş anlamlılar": "synonyms",
    "zıt anlamlılar": "antonyms",
    "zıt anlamlı": "antonyms",
    "alt kavramlar": "hyponyms",
}


def extract_gloss_list_linkage_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    l_list = []
    for span_tag in expanded_node.find_html("span"):
        if word_entry.lang_code == span_tag.attrs.get("lang", ""):
            l_data = Linkage(
                word=clean_node(wxr, None, span_tag),
                sense=" ".join(
                    word_entry.senses[-1].glosses
                    if len(word_entry.senses) > 0
                    else ""
                ),
            )
            if l_data.word != "":
                l_list.append(l_data)
        elif "Latn" in span_tag.attrs.get("class", "") and len(l_list) > 0:
            l_list[-1].roman = clean_node(wxr, None, span_tag)
    getattr(
        word_entry, GLOSS_LIST_LINKAGE_TEMPLATES[t_node.template_name]
    ).extend(l_list)
