from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name == "ku-IPA":
                    extract_ku_ipa_template(wxr, word_entry, t_node)
                elif t_node.template_name == "deng":
                    extract_deng_template(wxr, word_entry, t_node)
                elif t_node.template_name == "ku-kîte":
                    extract_ku_kîte(wxr, word_entry, t_node)


def extract_ku_ipa_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="IPA"
    ):
        sound = Sound(ipa=clean_node(wxr, None, span_tag))
        if sound.ipa != "":
            word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, expanded_node)


def extract_deng_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    sound = Sound(
        ipa=clean_node(wxr, None, t_node.template_parameters.get("ipa", ""))
    )
    raw_tag = clean_node(
        wxr,
        None,
        t_node.template_parameters.get(
            4, t_node.template_parameters.get("dever", "")
        ),
    )
    if raw_tag != "":
        sound.raw_tags.append(raw_tag)
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if filename != "":
        set_sound_file_url_fields(wxr, filename, sound)
        word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, t_node)


def extract_ku_kîte(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for index, node in enumerate(expanded_node.children):
        if isinstance(node, str) and ":" in node:
            hyphenation = clean_node(
                wxr,
                None,
                [node[node.index(":") + 1 :]]
                + expanded_node.children[index + 1 :],
            ).strip()
            if hyphenation != "":
                word_entry.hyphenation = hyphenation
            break
