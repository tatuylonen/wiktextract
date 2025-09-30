from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Form, Hyphenation, Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            for node in list_item.children:
                if isinstance(node, TemplateNode):
                    if node.template_name == "IPA":
                        extract_ipa_template(wxr, base_data, node, raw_tags)
                        raw_tags.clear()
                    elif node.template_name == "IPA2":
                        extract_ipa2_template(wxr, base_data, node, raw_tags)
                        raw_tags.clear()
                    elif node.template_name == "Audio":
                        extract_audio_template(wxr, base_data, node, raw_tags)
                        raw_tags.clear()
                    elif node.template_name == "Příznak2":
                        raw_tags.extend(extract_příznak2_template(wxr, node))
                elif (
                    isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC
                ):
                    raw_tag = clean_node(wxr, None, node)
                    if raw_tag != "":
                        raw_tags.append(raw_tag)


def extract_ipa_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
):
    # https://cs.wiktionary.org/wiki/Šablona:IPA
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="IPA"
    ):
        text = clean_node(wxr, None, span_tag)
        for ipa in text.split(","):
            ipa = ipa.strip()
            if ipa != "":
                sound = Sound(ipa=ipa, raw_tags=raw_tags)
                translate_raw_tags(sound)
                base_data.sounds.append(sound)
    clean_node(wxr, base_data, expanded_node)


def extract_ipa2_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
):
    # https://cs.wiktionary.org/wiki/Šablona:IPA2
    ipa = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if ipa != "":
        sound = Sound(ipa=f"[{ipa}]", raw_tags=raw_tags)
        translate_raw_tags(sound)
        base_data.sounds.append(sound)


def extract_audio_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
):
    # https://cs.wiktionary.org/wiki/Šablona:Audio
    file = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if file != "":
        sound = Sound(raw_tags=raw_tags)
        set_sound_file_url_fields(wxr, file, sound)
        translate_raw_tags(sound)
        base_data.sounds.append(sound)


def extract_příznak2_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[str]:
    raw_tags = []
    text = clean_node(wxr, None, t_node).strip("() ")
    for raw_tag in text.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            raw_tags.append(raw_tag)
    return raw_tags


def extract_hyphenation_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            h_str = clean_node(wxr, None, list_item.children)
            h_parts = list(filter(None, map(str.strip, h_str.split("-"))))
            if len(h_parts) > 0:
                base_data.hyphenations.append(Hyphenation(parts=h_parts))


def extract_homophone_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for link_node in list_item.find_child(NodeKind.LINK):
                homophone = clean_node(wxr, None, link_node)
                if homophone != "":
                    base_data.sounds.append(Sound(homophone=homophone))


def extract_transcript_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for index, node in enumerate(list_item.children):
                if isinstance(node, TemplateNode) and node.template_name in [
                    "Hiragana",
                    "Rómadži",
                    "Kana",
                ]:
                    extract_ja_transcript_template(wxr, word_entry, node)
                elif (
                    isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC
                ):
                    italic_str = clean_node(wxr, None, node).removesuffix(":")
                    if italic_str != "":
                        sound = Sound(raw_tags=[italic_str])
                        if italic_str in ["Pinyin", "Bopomofo"]:
                            sound.zh_pron = clean_node(
                                wxr, None, list_item.children[index + 1 :]
                            )
                        else:
                            sound.other = clean_node(
                                wxr, None, list_item.children[index + 1 :]
                            )
                        translate_raw_tags(sound)
                        word_entry.sounds.append(sound)
                        break


def extract_ja_transcript_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_template.find_html("span"):
        span_class = span_tag.attrs.get("class", "")
        if not span_class.endswith("-title") and span_class != "":
            span_text = clean_node(wxr, None, span_tag)
            if span_text != "":
                form = Form(form=span_text, raw_tags=[span_class])
                translate_raw_tags(form)
                word_entry.forms.append(form)
    clean_node(wxr, word_entry, expanded_template)
