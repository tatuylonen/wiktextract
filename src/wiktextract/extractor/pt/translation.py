import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    sense = ""
    sense_index = 0
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        match node.kind:
            case NodeKind.TEMPLATE:
                if node.template_name == "tradini":
                    sense, sense_index = extract_tradini_template(wxr, node)
            case NodeKind.LIST:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_translation_list_item(
                        wxr, word_entry, list_item, sense, sense_index
                    )


def extract_tradini_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[str, str]:
    # https://pt.wiktionary.org/wiki/Predefinição:tradini
    sense = ""
    sense_index = 0
    first_arg_str = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    m = re.match(r"De (\d+)", first_arg_str)
    if m is not None:
        sense_index = int(m.group(1))
        sense = first_arg_str[m.end() :].strip("() ")
    else:
        sense = first_arg_str
    return sense, sense_index


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    sense_index: int,
) -> None:
    translations = []
    lang_name = "unknown"
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            link_str = clean_node(wxr, None, node)
            if "/traduções" in link_str or "/tradução" in link_str:
                extract_translation_subpage(wxr, word_entry, link_str)
            elif lang_name == "unknown":
                lang_name = link_str
        elif isinstance(node, TemplateNode):
            match node.template_name:
                case "trad":
                    translations.extend(
                        extract_trad_template(wxr, node, sense, sense_index)
                    )
                case "trad-":
                    translations.extend(
                        extract_trad_minus_template(
                            wxr, node, sense, sense_index
                        )
                    )
                case "t":
                    translations.extend(
                        extract_t_template(wxr, node, sense, sense_index)
                    )
                case "xlatio":
                    translations.extend(
                        extract_xlatio_template(
                            wxr,
                            node,
                            sense,
                            sense_index,
                            translations[-1].lang
                            if len(translations) > 0
                            else lang_name,
                        )
                    )
        elif isinstance(node, str) and re.search(r"\(.+\)", node) is not None:
            roman = node.strip("() \n")
            for tr_data in translations:
                tr_data.roman = roman
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and len(translations) > 0
        ):
            raw_tag = clean_node(wxr, None, node)
            if raw_tag != "":
                translations[-1].raw_tags.append(raw_tag)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, next_list_item, sense, sense_index
                )

    word_entry.translations.extend(translations)


def extract_trad_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: str, sense_index: int
) -> list[Translation]:
    # https://pt.wiktionary.org/wiki/Predefinição:trad
    translations = []
    roman = clean_node(wxr, None, t_node.template_parameters.get("t", ""))
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    lang_name = "unknown"
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        lang_name = clean_node(wxr, None, link_node)
        break
    for arg in range(2, 12):
        if arg not in t_node.template_parameters:
            break
        tr_str = clean_node(wxr, None, t_node.template_parameters.get(arg, ""))
        if tr_str != "":
            translations.append(
                Translation(
                    word=tr_str,
                    lang=lang_name,
                    lang_code=lang_code,
                    roman=roman,
                    sense=sense,
                    sense_index=sense_index,
                )
            )
    return translations


def extract_trad_minus_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: str, sense_index: int
) -> list[Translation]:
    # https://pt.wiktionary.org/wiki/Predefinição:trad-
    translations = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    lang_name = "unknown"
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        lang_name = clean_node(wxr, None, link_node)
        break
    tr_data = Translation(
        word=clean_node(wxr, None, t_node.template_parameters.get(2, "")),
        lang=lang_name,
        lang_code=lang_code,
        roman=clean_node(
            wxr, None, t_node.template_parameters.get(3, "")
        ).strip("() "),
        sense=sense,
        sense_index=sense_index,
    )
    if tr_data.word != "":
        translations.append(tr_data)
    return translations


TRANSLATION_GENDER_TAGS = {
    "c": "common",
    "f": "feminine",
    "m": "masculine",
    "n": "neuter",
}


def extract_t_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: str, sense_index: int
) -> list[Translation]:
    # https://pt.wiktionary.org/wiki/Predefinição:t
    translations = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    lang_name = "unknown"
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        lang_name = clean_node(wxr, None, link_node)
        break
    tr_data = Translation(
        word=clean_node(wxr, None, t_node.template_parameters.get(2, "")),
        lang=lang_name,
        lang_code=lang_code,
        roman=clean_node(
            wxr, None, t_node.template_parameters.get(4, "")
        ).strip("() "),
        sense=sense,
        sense_index=sense_index,
    )
    gender_arg = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
    if gender_arg in TRANSLATION_GENDER_TAGS:
        tr_data.tags.append(TRANSLATION_GENDER_TAGS[gender_arg])
    if tr_data.word != "":
        translations.append(tr_data)
    return translations


def extract_xlatio_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: str,
    sense_index: int,
    lang_name: str,
) -> list[Translation]:
    # https://pt.wiktionary.org/wiki/Predefinição:xlatio
    translations = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    tr_data = Translation(
        word=clean_node(wxr, None, t_node.template_parameters.get(2, "")),
        lang=lang_name,
        lang_code=lang_code,
        sense=sense,
        sense_index=sense_index,
    )
    third_arg = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
    if third_arg.strip(".") in TRANSLATION_GENDER_TAGS:
        tr_data.tags.append(TRANSLATION_GENDER_TAGS[third_arg.strip(".")])
    else:
        tr_data.roman = third_arg.strip("() ")
    if tr_data.word != "":
        translations.append(tr_data)
    return translations


def extract_translation_subpage(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    page = wxr.wtp.get_page(page_title, 0)
    if page is not None and page.body is not None:
        root = wxr.wtp.parse(page.body)
        extract_translation_section(wxr, word_entry, root)
