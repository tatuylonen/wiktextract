from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry

# translate table row header to sound model field
PRON_GRAF_HEADER_MAP = {
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
        elif header_text == "silabación":
            word_entry.hyphenation = value_text
        elif header_text in PRON_GRAF_HEADER_MAP:
            sound = Sound()
            setattr(sound, PRON_GRAF_HEADER_MAP[header_text], value_text)
            word_entry.sounds.append(sound)
        elif (
            header_text.endswith(" alternativas") or header_text == "variantes"
        ):
            process_pron_graf_link_cell(
                wxr, word_entry, value_node, header_text, "alternative"
            )
        elif header_text == "homófonos":
            process_pron_graf_link_cell(
                wxr, word_entry, value_node, header_text, "homophone"
            )
        elif header_text == "transliteraciones":
            process_pron_graf_text_cell(wxr, word_entry, value_node, "roman")
        elif header_text == "transcripciones silábicas":
            process_pron_graf_text_cell(wxr, word_entry, value_node, "syllabic")
        else:
            extra_sounds[header_text] = value_text

    if len(extra_sounds) > 0:
        word_entry.extra_sounds = extra_sounds
    clean_node(wxr, word_entry, expanded_node)


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
            set_sound_file_url_fields(wxr, sound_file, sound)
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


def process_pron_graf_link_cell(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    cell_node: WikiNode,
    header_text: str,
    field_name: str,
) -> None:
    for link_index, link_node in cell_node.find_child(
        NodeKind.LINK, with_index=True
    ):
        sound = Sound()
        setattr(sound, field_name, clean_node(wxr, None, link_node))
        if (
            link_index + 1 < len(cell_node.children)
            and isinstance(cell_node.children[link_index + 1], HTMLNode)
            and cell_node.children[link_index + 1].tag == "ref"
        ):
            # nest "ref" tag is note text
            sound.note = clean_node(
                wxr, None, cell_node.children[link_index + 1].children
            )
        if header_text == "variantes":
            sound.not_same_pronunciation = True
        word_entry.sounds.append(sound)


def process_pron_graf_text_cell(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    cell_node: WikiNode,
    field_name: str,
) -> None:
    sound = Sound()
    for node_index, node in enumerate(cell_node.children):
        if isinstance(node, str) and len(node.strip()) > 0:
            node = node.strip()
            if node.startswith(",&nbsp;"):
                node = node.removeprefix(",&nbsp;")
                word_entry.sounds.append(sound.model_copy(deep=True))
                sound = Sound()
            setattr(sound, field_name, node.strip())
        elif isinstance(node, HTMLNode) and node.tag == "ref":
            sound.note = clean_node(wxr, None, node.children)
    if len(getattr(sound, field_name)) > 0:
        word_entry.sounds.append(sound)
