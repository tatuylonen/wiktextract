from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import HTMLNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import create_audio_url_dict
from .models import AlterSound, Sound, WordEntry

# translate table row header to sound model field
PRON_GRAF_HEADER_MAP = {
    "silabación": "syllabic",
    "transcripciones silábicas": "syllabic",
    "rimas": "rhymes",
    "rima": "rhymes",
}


def process_pron_graf_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:pron-graf
    # this template could create sound data without any parameter
    # it expands to a two columns table
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    non_ipa_sound = Sound()  # combine non-ipa data to this object
    extra_sounds = {}  # not translated
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        table_cells = list(table_row.find_child(NodeKind.TABLE_CELL))
        if len(table_cells) != 2:
            continue
        header_node, value_node = table_cells
        header_text = clean_node(wxr, None, header_node)
        value_text = clean_node(wxr, None, value_node)
        if header_text.endswith(" (AFI)"):  # IPA
            process_pron_graf_ipa_cell(wxr, word_entry, value_node, header_text)
        elif header_text in PRON_GRAF_HEADER_MAP:
            prev_value = getattr(
                non_ipa_sound, PRON_GRAF_HEADER_MAP[header_text]
            )
            prev_value.append(value_text)
        elif (
            header_text.endswith(" alternativas") or header_text == "variantes"
        ):
            process_pron_graf_alt_cell(
                wxr, non_ipa_sound, value_node, header_text
            )
        else:
            extra_sounds[header_text] = value_text

    if non_ipa_sound != Sound():
        word_entry.sounds.append(non_ipa_sound)
    if len(extra_sounds) > 0:
        word_entry.extra_sounds = extra_sounds


def process_pron_graf_ipa_cell(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    cell_node: WikiNode,
    header_text: str,
) -> None:
    sound = Sound()
    for node in cell_node.children:
        if isinstance(node, str) and len(node.strip()) > 0:
            sound.ipa += node.strip()
        elif isinstance(node, HTMLNode) and node.tag == "phonos":
            sound_file = node.attrs.get("file", "")
            sound_urls = create_audio_url_dict(sound_file)
            for sound_key, sound_value in sound_urls.items():
                if hasattr(sound, sound_key):
                    setattr(sound, sound_key, sound_value)
            for small_tag in node.find_html("small"):
                location = clean_node(wxr, None, small_tag)
                sound.raw_tags.append(location)
        elif (
            isinstance(node, HTMLNode) and node.tag == "br" and sound != Sound()
        ):
            if not header_text.startswith("pronunciación"):  # location
                sound.raw_tags.append(header_text.removesuffix(" (AFI)"))
            word_entry.sounds.append(sound.model_copy(deep=True))
            sound = Sound()
    if sound != Sound():
        if not header_text.startswith("pronunciación"):
            sound.raw_tags.append(header_text.removesuffix(" (AFI)"))
        word_entry.sounds.append(sound)


def process_pron_graf_alt_cell(
    wxr: WiktextractContext, sound: Sound, cell_node: WikiNode, header_text: str
) -> None:
    for link_index, alt_link in cell_node.find_child(
        NodeKind.LINK, with_index=True
    ):
        alt_sound = AlterSound(word=clean_node(wxr, None, alt_link))
        if (
            link_index + 1 < len(cell_node.children)
            and isinstance(cell_node.children[link_index + 1], HTMLNode)
            and cell_node.children[link_index + 1].tag == "ref"
        ):
            # nest "ref" tag is note text
            alt_sound.note = clean_node(
                wxr, None, cell_node.children[link_index + 1].children
            )
        if header_text == "variantes":
            alt_sound.not_same_pronunciation = True
        sound.alternatives.append(alt_sound)


def process_audio_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://es.wiktionary.org/wiki/Plantilla:audio
    sound = Sound()
    audio = template_node.template_parameters.get(1)
    if audio:
        audio_url_dict = create_audio_url_dict(audio)
        for dict_key, dict_value in audio_url_dict.items():
            if dict_value and dict_key in sound.model_fields:
                setattr(sound, dict_key, dict_value)

    # XXX: Extract other parameters from the Spanish audio template

    if len(sound.model_dump(exclude_defaults=True)) > 0:
        word_entry.sounds.append(sound)
