from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    sounds = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sounds.extend(extract_sound_list_item(wxr, list_item))
    for node in level_node.find_child(NodeKind.TEMPLATE):
        extract_sound_templates(wxr, node, [])

    if len(page_data) == 0:
        for sound in sounds:
            if sound.hyphenation != "":
                base_data.hyphenation = sound.hyphenation
            else:
                base_data.sounds.append(sound)
            for cat in sound.categories:
                if cat not in base_data:
                    base_data.categories.append(cat)
    elif level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                for sound in sounds:
                    if sound.hyphenation != "":
                        data.hyphenation = sound.hyphenation
                    else:
                        data.sounds.append(sound)
                    for cat in sound.categories:
                        if cat not in data.categories:
                            data.categories.append(cat)
    else:
        for sound in sounds:
            if sound.hyphenation != "":
                page_data[-1].hyphenation = sound.hyphenation
            else:
                page_data[-1].sounds.append(sound)
            for cat in sound.categories:
                if cat not in page_data[-1].categories:
                    page_data[-1].categories.append(cat)


def extract_sound_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Sound]:
    raw_tags = []
    cats = {}
    sounds = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["a", "accent"]:
                raw_tag = clean_node(wxr, cats, node).strip("() ")
                if raw_tag != "":
                    raw_tags.append(raw_tag)
            else:
                sounds.extend(extract_sound_templates(wxr, node, raw_tags))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                sounds.extend(extract_sound_list_item(wxr, child_list_item))
        elif isinstance(node, str) and node.strip().endswith(":"):
            raw_tag = node.strip(": ")
            if raw_tag != "":
                raw_tags.append(raw_tag)
    for sound in sounds:
        sound.categories.extend(cats.get("categories", []))
    return sounds


def extract_sound_templates(
    wxr: WiktextractContext, t_node: TemplateNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    if t_node.template_name == "dewan":
        sounds.extend(extract_dewan_template(wxr, t_node))
    elif t_node.template_name in ["audio-AFA", "audio-IPA"]:
        sounds.extend(extract_audio_ipa_template(wxr, t_node, raw_tags))
    elif t_node.template_name.lower() in [
        "afa",
        "ipa",
    ] or t_node.template_name.lower().endswith(("-afa", "-ipa")):
        sounds.extend(extract_ipa_template(wxr, t_node, raw_tags))
    elif t_node.template_name in ["penyempangan", "hyphenation", "hyph"]:
        sounds.extend(extract_hyph_template(wxr, t_node))
    elif t_node.template_name == "audio":
        sounds.extend(extract_audio_template(wxr, t_node))
    elif t_node.template_name in ["rima", "rhymes", "rhyme"]:
        sounds.extend(extract_rhyme_template(wxr, t_node))
    return sounds


def extract_dewan_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Sound]:
    sounds = []
    cats = {}
    text = clean_node(wxr, cats, t_node).removeprefix("Kamus Dewan:").strip()
    if text != "":
        sounds.append(
            Sound(
                other=text,
                raw_tags=["Kamus Dewan"],
                categories=cats.get("categories", []),
            )
        )
    return sounds


def extract_ipa_template(
    wxr: WiktextractContext, t_node: TemplateNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    cats = {}
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    clean_node(wxr, cats, expanded_template)
    for span_tag in expanded_template.find_html(
        "span", attr_name="class", attr_value="IPA"
    ):
        ipa = clean_node(wxr, None, span_tag)
        if ipa != "":
            sound = Sound(
                ipa=ipa,
                raw_tags=raw_tags,
                categories=cats.get("categories", []),
            )
            translate_raw_tags(sound)
            sounds.append(sound)
    return sounds


def extract_hyph_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Sound]:
    sounds = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_template.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        text = clean_node(wxr, None, span_tag)
        if text != "":
            sounds.append(Sound(hyphenation=text))
    return sounds


def extract_audio_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Sound]:
    sounds = []
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    cats = {}
    clean_node(wxr, cats, t_node)
    if filename != "":
        sound = Sound(categories=cats.get("categories", []))
        set_sound_file_url_fields(wxr, filename, sound)
        sounds.append(sound)
    return sounds


def extract_rhyme_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Sound]:
    sounds = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    cats = {}
    clean_node(wxr, cats, expanded_template)
    for link in expanded_template.find_child(NodeKind.LINK):
        sound = Sound(categories=cats.get("categories", []))
        text = clean_node(wxr, None, link)
        if text != "":
            sound.rhymes = text
            sounds.append(sound)
    return sounds


def extract_audio_ipa_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> list[Sound]:
    sounds = []
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    cats = {}
    clean_node(wxr, cats, t_node)
    if filename != "":
        ipa = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
        sound = Sound(ipa=ipa, categories=cats.get("categories", []))
        set_sound_file_url_fields(wxr, filename, sound)
        sounds.append(sound)
    return sounds
