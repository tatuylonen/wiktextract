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
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in ["ARchar", "Arab", "PSchar", "SDchar"]:
            word = clean_node(wxr, None, t_node)
            if word != "":
                word_entry.forms.append(Form(form=word, tags=tags))


def extract_linkage_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item)


def extract_linkage_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    linkage_name = clean_node(wxr, None, list_item.children)
    if linkage_name not in LINKAGE_SECTIONS:
        return
    for node in list_item.definition:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                getattr(word_entry, LINKAGE_SECTIONS[linkage_name]).append(
                    Linkage(word=word)
                )
        elif isinstance(node, str):
            for word in node.split(","):
                word = word.strip(" .\n")
                if word != "":
                    getattr(word_entry, LINKAGE_SECTIONS[linkage_name]).append(
                        Linkage(word=word)
                    )


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
