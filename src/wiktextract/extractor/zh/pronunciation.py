import itertools

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, HTMLNode, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import create_audio_url_dict, set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    from .page import parse_section

    # process POS section first
    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        process_pron_template(wxr, page_data, template_node)
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_pron_item_list_item(wxr, page_data, list_item_node)


def process_pron_item_list_item(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_item_node: WikiNode,
) -> None:
    raw_tags = []
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        process_pron_template(wxr, page_data, template_node, raw_tags)


def process_pron_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    raw_tags: list[str] = [],
):
    template_name = template_node.template_name.lower()
    if template_name == "zh-pron":
        process_zh_pron_template(wxr, page_data, template_node)
    elif template_name in ["homophones", "homophone", "hmp"]:
        process_homophones_template(wxr, page_data, template_node)
    elif template_name in ["a", "accent"]:
        # https://zh.wiktionary.org/wiki/Template:Accent
        raw_tags.append(clean_node(wxr, None, template_node).strip("()"))
    elif template_name in ["audio", "音"]:
        process_audio_template(wxr, page_data, template_node, raw_tags)
    elif template_name == "ipa":
        process_ipa_template(wxr, page_data, template_node, raw_tags)
    elif template_name == "enpr":
        process_enpr_template(wxr, page_data, template_node, raw_tags)


def process_zh_pron_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
):
    # https://zh.wiktionary.org/wiki/Template:Zh-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    seen_lists = set()
    for list_node in expanded_node.find_child_recursively(NodeKind.LIST):
        if list_node not in seen_lists:
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                process_zh_pron_list_item(
                    wxr, page_data, list_item, [], seen_lists
                )


def process_zh_pron_list_item(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_item_node: WikiNode,
    raw_tags: list[str],
    seen_lists: set[WikiNode],
):
    current_tags = raw_tags[:]
    for node in list_item_node.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                if len(node.largs) > 0 and node.largs[0][0].startswith("File:"):
                    sound_file_data = create_audio_url_dict(
                        node.largs[0][0].removeprefix("File:")
                    )
                    sound_data = Sound()
                    for key, value in sound_file_data.items():
                        if key in Sound.model_fields:
                            setattr(sound_data, key, value)
                        else:
                            wxr.wtp.warning(
                                f"{key=} not defined in Sound",
                                sortid="zh.pronunciation/56",
                            )
                    page_data[-1].sounds.append(sound_data)
                else:
                    current_tags.append(clean_node(wxr, None, node).strip("()"))
            elif isinstance(node, HTMLNode):
                if node.tag == "small":
                    # remove "幫助"(help) <sup> tag
                    current_tags.append(
                        clean_node(
                            wxr,
                            None,
                            list(node.invert_find_child(NodeKind.HTML)),
                        ).strip("()")
                    )
                elif node.tag == "span":
                    zh_pron = clean_node(wxr, None, node)
                    if len(zh_pron) > 0:
                        if "IPA" in node.attrs.get("class", ""):
                            sound = Sound(ipa=zh_pron, raw_tags=current_tags)
                        else:
                            sound = Sound(
                                zh_pron=zh_pron, raw_tags=current_tags
                            )
                        page_data[-1].sounds.append(sound)
                elif (
                    node.tag == "table"
                    and len(current_tags) > 0
                    and current_tags[-1] == "同音詞"
                ):
                    process_homophones_table(wxr, page_data, node, current_tags)

            elif node.kind == NodeKind.LIST:
                seen_lists.add(node)
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    process_zh_pron_list_item(
                        wxr, page_data, next_list_item, current_tags, seen_lists
                    )


def process_homophones_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
):
    # https://zh.wiktionary.org/wiki/Template:homophones
    for word_index in itertools.count(2):
        if word_index not in template_node.template_parameters:
            break
        homophone = clean_node(
            wxr, None, template_node.template_parameters.get(word_index, "")
        )
        if len(homophone) > 0:
            page_data[-1].sounds.append(Sound(homophone=homophone))


def process_homophones_table(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    table_node: HTMLNode,
    raw_tags: list[str],
) -> None:
    for span_node in table_node.find_html_recursively("span", attr_name="lang"):
        sound_data = Sound(
            homophone=clean_node(wxr, None, span_node), raw_tags=raw_tags
        )
        page_data[-1].sounds.append(sound_data)


def process_audio_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Audio
    sound_file = clean_node(
        wxr, None, template_node.template_parameters.get(2, "")
    )
    sound_data = Sound()
    set_sound_file_url_fields(wxr, sound_file, sound_data)
    raw_tag = clean_node(
        wxr, None, template_node.template_parameters.get(3, "")
    )
    if len(raw_tag) > 0:
        sound_data.raw_tags.append(raw_tag)
    sound_data.raw_tags.extend(raw_tags)
    page_data[-1].sounds.append(sound_data)


def process_ipa_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:IPA
    for index in itertools.count(2):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            ipa=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        page_data[-1].sounds.append(sound)


def process_enpr_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:enPR
    for index in range(1, 4):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            enpr=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        page_data[-1].sounds.append(sound)
