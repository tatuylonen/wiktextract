import re

from mediawiki_langcodes import code_to_name, name_to_code
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "Ü-Tabelle":
            process_u_tabelle_template(wxr, word_entry, template_node)


def process_u_tabelle_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Ü-Tabelle
    sense_idx = clean_node(
        wxr, None, template_node.template_parameters.get(1, "")
    )
    sense = clean_node(
        wxr, None, template_node.template_parameters.get("G", "")
    )
    for list_arg_name in ["Ü-Liste", "Dialekttabelle"]:
        list_arg_value = template_node.template_parameters.get(list_arg_name)
        if list_arg_value is None:
            continue
        tr_list = wxr.wtp.parse(wxr.wtp.node_to_wikitext(list_arg_value))
        for list_item in tr_list.find_child_recursively(NodeKind.LIST_ITEM):
            process_u_tabelle_list_item(
                wxr, word_entry, list_item, sense, sense_idx
            )


def process_u_tabelle_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item_node: WikiNode,
    sense: str,
    sense_idx: str,
) -> None:
    before_colon = True
    tr_data = Translation(sense=sense, sense_index=sense_idx)
    for node in list_item_node.children:
        if isinstance(node, str):
            node = node.strip()
            if len(node) == 0:
                continue
            elif ":" in node:
                lang_str = node[: node.index(":")].strip()
                if len(lang_str) > 0 and len(tr_data.lang) == 0:
                    tr_data.lang = lang_str
                    if len(tr_data.lang_code) == 0:
                        tr_data.lang_code = name_to_code(lang_str, "de")
                before_colon = False
            elif node in [",", ";"] and len(tr_data.word) > 0:
                tr_data = append_tr_data(word_entry, tr_data)

        if before_colon and len(tr_data.lang) == 0:
            tr_data.lang = clean_node(wxr, None, node)
            if isinstance(node, TemplateNode):
                tr_data.lang_code = node.template_name.lower()
            else:
                tr_data.lang_code = name_to_code(tr_data.lang_code, "de")
        elif isinstance(node, TemplateNode):
            if node.template_name.startswith("Ü"):
                if len(tr_data.word) > 0:
                    tr_data = append_tr_data(word_entry, tr_data)
                process_u_template(wxr, tr_data, node)
            else:
                raw_tag = clean_node(wxr, None, node).strip(": \n")
                if raw_tag != "":
                    tr_data.raw_tags.append(raw_tag)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            raw_tag_str = clean_node(wxr, None, node).removesuffix(":")
            for raw_tag in filter(None, raw_tag_str.split(", ")):
                tr_data.raw_tags.append(raw_tag)

    if len(tr_data.word) > 0:
        append_tr_data(word_entry, tr_data)


def append_tr_data(word_entry: WordEntry, tr_data: Translation) -> Translation:
    translate_raw_tags(tr_data)
    word_entry.translations.append(tr_data.model_copy(deep=True))
    return Translation(
        sense=tr_data.sense,
        sense_index=tr_data.sense_index,
        lang=tr_data.lang,
        lang_code=tr_data.lang_code,
    )


def process_u_template(
    wxr: WiktextractContext, tr_data: Translation, u_template: TemplateNode
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Ü
    # also "Ü?", "Üt", "Üt?", "Üxx4", "Üxx4?"
    if len(tr_data.lang_code) == 0:
        tr_data.lang_code = clean_node(
            wxr, None, u_template.template_parameters.get(1, "")
        )
    if len(tr_data.lang) == 0:
        tr_data.lang = code_to_name(tr_data, "de")

    tr_data.word = clean_node(
        wxr, None, u_template.template_parameters.get(2, "")
    )
    template_name = u_template.template_name
    tr_data.uncertain = template_name.endswith("?")
    template_name = template_name.removesuffix("?")
    display_arg = -1
    if template_name == "Ü":
        display_arg = 3
    elif template_name == "Üt":
        display_arg = 4
        if 3 in u_template.template_parameters:
            arg_value = clean_node(
                wxr, None, u_template.template_parameters.get(3, "")
            )
            if tr_data.lang_code in ["ja", "ko"] and "," in arg_value:
                tr_data.other, tr_data.roman = tuple(
                    map(str.strip, arg_value.split(",", maxsplit=1))
                )
            else:
                tr_data.roman = arg_value
        else:
            # this template could create roman without the third arg
            expanded_text = clean_node(wxr, None, u_template)
            m = re.search(r"\(([^)]+?)\^\☆\)", expanded_text)
            if m is not None:
                tr_data.roman = m.group(1)
    elif template_name == "Üxx4":
        display_arg = "v"
        if 3 in u_template.template_parameters:
            display_arg = 3
        tr_data.roman = clean_node(
            wxr, None, u_template.template_parameters.get("d", "")
        )

    tr_word = clean_node(
        wxr, None, u_template.template_parameters.get(display_arg, "")
    )
    if len(tr_word) > 0:
        tr_data.word = tr_word
