from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import HTMLNode, TemplateNode
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Sound, WordEntry


def process_pron_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
):
    if template_node.template_name == "zh-pron":
        process_zh_pron(wxr, page_data, template_node)


def process_zh_pron(
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
            elif node.kind == NodeKind.LIST:
                seen_lists.add(node)
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    process_zh_pron_list_item(
                        wxr, page_data, next_list_item, current_tags, seen_lists
                    )
