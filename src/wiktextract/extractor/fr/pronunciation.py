from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Sound, WordEntry


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    base_data: WordEntry,
) -> None:
    sound_data = []
    lang_code = base_data.lang_code
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
            sound_data.extend(
                process_pron_list_item(wxr, list_item_node, Sound(), lang_code)
            )

    if len(sound_data) == 0:
        return
    if len(page_data) == 0:
        page_data.append(base_data.model_copy(deep=True))

    if level_node.kind == NodeKind.LEVEL3:
        # Add extracted sound data to all sense dictionaries that have the same
        # language code when the prononciation subtitle is a level 3 title node.
        # Otherwise only add to the last one.
        for sense_data in page_data:
            if sense_data.lang_code == lang_code:
                sense_data.sounds.extend(sound_data)
    else:
        page_data[-1].sounds.extend(sound_data)


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
    sound_data: Sound,
    lang_code: str,
) -> list[Sound]:
    pron_key = "zh_pron" if lang_code == "zh" else "ipa"

    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in PRON_TEMPLATES:
            pron_text = process_pron_template(wxr, template_node)
            if len(pron_text) > 0:
                setattr(sound_data, pron_key, pron_text)
        elif template_node.template_name in {"écouter", "audio", "pron-rég"}:
            process_ecouter_template(wxr, template_node, sound_data)
        else:
            sound_tag = clean_node(wxr, None, template_node)
            if sound_tag.startswith("(") and sound_tag.endswith(")"):
                sound_tag = sound_tag.strip("()")
            sound_data.tags.append(sound_tag)

    if list_item_node.contain_node(NodeKind.LIST):
        returned_data = []
        for bold_node in list_item_node.find_child(NodeKind.BOLD):
            sound_data.tags.append(clean_node(wxr, None, bold_node))

        for nest_list_item in list_item_node.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            new_sound_data = sound_data.model_copy(deep=True)
            process_pron_list_item(
                wxr, nest_list_item, new_sound_data, lang_code
            )
            if pron_key in new_sound_data.model_fields_set:
                returned_data.append(new_sound_data)

        return returned_data
    elif len(sound_data.model_dump(exclude_defaults=True)) > 0:
        if pron_key not in sound_data.model_fields_set:
            for child in list_item_node.filter_empty_str_child():
                if isinstance(child, str):
                    if child.strip().startswith(": "):
                        # IPA text after "language : "
                        setattr(
                            sound_data,
                            pron_key,
                            child.strip().removeprefix(": ").strip(),
                        )
                    elif len(child.strip()) > 0 and child.strip() != ":":
                        # language text before ":"
                        sound_data.tags.append(child.strip())

        if len({pron_key, "audio"} & sound_data.model_fields_set) > 0:
            return [sound_data]
    return []


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
    sound_data: Sound,
) -> None:
    # sound file template: https://fr.wiktionary.org/wiki/Modèle:écouter
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
    if len(location) > 0:
        sound_data.tags.append(location)
    if len(ipa) > 0:
        sound_data.ipa = ipa
    if len(audio_file) > 0:
        audio_data = create_audio_url_dict(audio_file)
        for key, value in audio_data.items():
            if key in sound_data.model_fields:
                setattr(sound_data, key, value)
            else:
                wxr.wtp.debug(
                    f"{key=} not defined in Sound",
                    sortid="fr.pronunciation/156",
                )


def is_ipa_text(text: str) -> bool:
    # check if the text is IPA, used for inflection table cell text
    if text.startswith("\\") and text.endswith("\\"):
        return True
    if text.startswith("ou ") and text.endswith("\\"):
        # some inflection table template like "en-nom-rég" might have a second
        # ipa text in a new line
        return True
    return False
