from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, word_entry, list_item)


def extract_sound_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["ku-IPA", "IPA-ku"]:
                extract_ku_ipa_template(wxr, word_entry, node)
            elif node.template_name in ["deng", "sound"]:
                extract_deng_template(wxr, word_entry, node)
            elif node.template_name == "ku-kîte":
                extract_ku_kîte(wxr, word_entry, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_sound_list_item(wxr, word_entry, child_list_item)


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
    for r_tag in raw_tag.split(","):
        r_tag = r_tag.strip()
        if r_tag != "":
            sound.raw_tags.append(r_tag)
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if filename != "":
        set_sound_file_url_fields(wxr, filename, sound)
        translate_raw_tags(sound)
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
                word_entry.hyphenations.append(
                    Hyphenation(parts=hyphenation.split("·"))
                )
            break
