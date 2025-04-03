from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sound, WordEntry
from .tags import translate_raw_tags
from ..share import set_sound_file_url_fields


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, word_entry, list_item)
    for node in level_node.find_child(NodeKind.TEMPLATE):
        extract_sound_templates(wxr, word_entry, node, [])


def extract_sound_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    raw_tags = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["a", "accent"]:
                raw_tag = clean_node(wxr, word_entry, node).strip("() ")
                if raw_tag != "":
                    raw_tags.append(raw_tag)
            else:
                extract_sound_templates(wxr, word_entry, node, raw_tags)


def extract_sound_templates(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    if t_node.template_name == "dewan":
        extract_dewan_template(wxr, word_entry, t_node)
    elif t_node.template_name.lower() in ["afa", "ipa"]:
        extract_ipa_template(wxr, word_entry, t_node, raw_tags)
    elif t_node.template_name in ["penyempangan", "hyphenation", "hyph"]:
        extract_hyph_template(wxr, word_entry, t_node)
    elif t_node.template_name == "audio":
        extract_audio_template(wxr, word_entry, t_node)
    elif t_node.template_name in ["rima", "rhymes", "rhyme"]:
        extract_rhyme_template(wxr, word_entry, t_node)


def extract_dewan_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    text = (
        clean_node(wxr, word_entry, t_node).removeprefix("Kamus Dewan:").strip()
    )
    if text != "":
        word_entry.sounds.append(Sound(other=text, raw_tags=["Kamus Dewan"]))


def extract_ipa_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_template.find_html(
        "span", attr_name="class", attr_value="IPA"
    ):
        ipa = clean_node(wxr, None, span_tag)
        if ipa != "":
            sound = Sound(ipa=ipa, raw_tags=raw_tags)
            translate_raw_tags(sound)
            word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, expanded_template)


def extract_hyph_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_template.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        text = clean_node(wxr, None, span_tag)
        if text != "":
            word_entry.hyphenation = text


def extract_audio_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if filename != "":
        sound = Sound()
        set_sound_file_url_fields(wxr, filename, sound)
        word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, t_node)


def extract_rhyme_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link in expanded_template.find_child(NodeKind.LINK):
        text = clean_node(wxr, word_entry, link)
        if text != "":
            word_entry.sounds.append(Sound(rhymes=text))
