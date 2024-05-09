import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    base_data: WordEntry,
) -> None:
    sounds_list = []
    lang_code = base_data.lang_code
    for node in level_node.find_child(
        NodeKind.LIST | LEVEL_KIND_FLAGS | NodeKind.TEMPLATE
    ):
        if node.kind == NodeKind.LIST:
            for list_item_node in node.find_child(NodeKind.LIST_ITEM):
                sounds_list.extend(
                    process_pron_list_item(wxr, list_item_node, [], lang_code)
                )
        elif isinstance(node, TemplateNode):
            if node.template_name in ["cmn-pron", "zh-cmn-pron"]:
                sounds_list.extend(process_cmn_pron_template(wxr, node))
        elif node.kind in LEVEL_KIND_FLAGS:
            from .page import parse_section

            parse_section(wxr, page_data, base_data, node)

    if len(sounds_list) == 0:
        return
    if len(page_data) == 0:
        page_data.append(base_data.model_copy(deep=True))

    if level_node.kind == NodeKind.LEVEL3:
        # Add extracted sound data to all sense dictionaries that have the same
        # language code when the prononciation subtitle is a level 3 title node.
        # Otherwise only add to the last one.
        for sense_data in page_data:
            if sense_data.lang_code == lang_code:
                sense_data.sounds.extend(sounds_list)
    else:
        page_data[-1].sounds.extend(sounds_list)


PRON_TEMPLATES = frozenset(
    [
        "pron",  # redirect to "prononciation"
        "prononciation",
        "//",  # redirect to "prononciation"
        "phon",  # redirect to "prononciation"
        "pron-recons",  # use "pron"
        "prononciation reconstruite",  # redirect to "pron-recons"
        "pron recons",  # redirect to "pron-recons"
        "lang",  # used in template "cmn-pron", which expands to list of Pinyin
    ]
)


def process_pron_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    parent_raw_tags: list[str],
    lang_code: str,
) -> list[Sound]:
    current_raw_tags = parent_raw_tags[:]
    sounds_list = []
    pron_key = "zh_pron" if lang_code == "zh" else "ipa"
    after_collon = False
    for child_index, list_item_child in enumerate(list_item_node.children):
        if isinstance(list_item_child, TemplateNode):
            if list_item_child.template_name in PRON_TEMPLATES:
                pron_texts = process_pron_template(wxr, list_item_child)
                if len(pron_texts) > 0:
                    use_key = (
                        "zh_pron"
                        if list_item_child.template_name == "lang"
                        else "ipa"
                    )
                    prons = set()
                    for pron_text in re.split(",|，", pron_texts):
                        pron_text = pron_text.strip()
                        if len(pron_text) > 0 and pron_text not in prons:
                            prons.add(pron_text)
                            sound = Sound()
                            setattr(sound, use_key, pron_text)
                            if len(current_raw_tags) > 0:
                                sound.raw_tags = current_raw_tags[:]
                            sounds_list.append(sound)

            elif list_item_child.template_name in {
                "écouter",
                "audio",
                "pron-rég",
            }:
                sounds_list.append(
                    process_ecouter_template(
                        wxr, list_item_child, current_raw_tags
                    )
                )
            elif list_item_child.template_name == "pron-rimes":
                sounds_list.append(
                    process_pron_rimes_template(
                        wxr, list_item_child, current_raw_tags
                    )
                )
            elif not after_collon:  # location
                raw_tag = clean_node(wxr, None, list_item_child)
                if len(raw_tag) > 0:
                    current_raw_tags.append(raw_tag)
        elif isinstance(list_item_child, WikiNode):
            if list_item_child.kind == NodeKind.BOLD:
                current_raw_tags.append(clean_node(wxr, None, list_item_child))
            elif list_item_child.kind == NodeKind.LINK:
                for span_tag in list_item_child.find_html_recursively("span"):
                    sound = Sound(ipa=clean_node(wxr, None, span_tag))
                    if len(current_raw_tags) > 0:
                        sound.raw_tags = current_raw_tags[:]
                    sounds_list.append(sound)
        elif isinstance(list_item_child, str):
            if ":" in list_item_child:
                after_collon = True
                pron_text = list_item_child[
                    list_item_child.find(":") + 1 :
                ].strip()
                if len(pron_text) > 0:
                    sound = Sound()
                    setattr(sound, pron_key, pron_text)
                    if len(current_raw_tags) > 0:
                        sound.raw_tags = current_raw_tags[:]
                    sounds_list.append(sound)

    for nest_list_item in list_item_node.find_child_recursively(
        NodeKind.LIST_ITEM
    ):
        sounds_list.extend(
            process_pron_list_item(
                wxr, nest_list_item, current_raw_tags, lang_code
            )
        )

    return sounds_list


def process_pron_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> str:
    if (
        template_node.template_name in PRON_TEMPLATES
        and isinstance(template_node.template_parameters.get(1, ""), str)
        and len(template_node.template_parameters.get(1, "")) == 0
    ):
        # some pages don't pass IPA parameter to the "pron" template
        # and expand to an edit link for adding the missing data.
        return ""
    return clean_node(wxr, None, template_node)


def process_ecouter_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> Sound:
    # sound file template: https://fr.wiktionary.org/wiki/Modèle:écouter
    sound = Sound()
    location = clean_node(
        wxr, None, template_node.template_parameters.get(1, "")
    )
    if location.startswith("(") and location.endswith(")"):
        location = location.strip("()")
    ipa = clean_node(
        wxr,
        None,
        template_node.template_parameters.get(
            2, template_node.template_parameters.get("pron", "")
        ),
    )
    audio_file = clean_node(
        wxr, None, template_node.template_parameters.get("audio", "")
    )
    if len(raw_tags) > 0:
        sound.raw_tags = raw_tags[:]
    if len(location) > 0:
        sound.raw_tags.append(location)
    if len(ipa) > 0:
        sound.ipa = ipa
    if len(audio_file) > 0:
        set_sound_file_url_fields(wxr, audio_file, sound)
    return sound


def is_ipa_text(text: str) -> bool:
    # check if the text is IPA, used for inflection table cell text
    if text.startswith("\\") and text.endswith("\\"):
        return True
    if text.startswith("ou ") and text.endswith("\\"):
        # some inflection table template like "en-nom-rég" might have a second
        # ipa text in a new line
        return True
    return False


def process_pron_rimes_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> Sound:
    # https://fr.wiktionary.org/wiki/Modèle:pron-rimes
    sound = Sound()
    sound.ipa = clean_node(
        wxr, None, template_node.template_parameters.get(1, "")
    )
    if len(raw_tags) > 0:
        sound.raw_tags = raw_tags[:]
    # this templates also has rhyme data, not sure where to put it
    return sound


def process_cmn_pron_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> list[Sound]:
    # https://fr.wiktionary.org/wiki/Modèle:cmn-pron
    sounds_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node),
        pre_expand=True,
        additional_expand={template_node.template_name},
    )
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sounds_list.extend(process_pron_list_item(wxr, list_item, [], "zh"))

    return sounds_list
