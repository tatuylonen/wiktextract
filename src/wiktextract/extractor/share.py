import hashlib
import re
from html import unescape
from typing import Iterable, Optional, Union

from wikitextprocessor import NodeKind, WikiNode


def strip_nodes(
    nodes: list[Union[WikiNode, str]],
) -> Iterable[Union[WikiNode, str]]:
    # filter nodes that only have newlines, white spaces and non-breaking spaces
    return filter(
        lambda node: isinstance(node, WikiNode)
        or (isinstance(node, str) and len(unescape(node).strip()) > 0),
        nodes,
    )


def capture_text_in_parentheses(text: str) -> tuple[list[str], str]:
    """
    Return a list of text inside parentheses, and the rest test.
    """
    rest_parts = []
    capture_text_list = []
    last_group_end = 0
    for m in re.finditer(r"\([^()]+\)", text):
        not_captured = text[last_group_end : m.start()].strip()
        if len(not_captured) > 0:
            rest_parts.append(not_captured)
        last_group_end = m.end()
        group_text = m.group()[1:-1].strip()
        if len(group_text) > 0:
            capture_text_list.append(group_text)
    not_captured = text[last_group_end:].strip()
    if len(not_captured) > 0:
        rest_parts.append(not_captured)
    rest_text = " ".join(rest_parts) if len(rest_parts) > 0 else text
    return capture_text_list, rest_text


def split_chinese_variants(text: str) -> Iterable[tuple[Optional[str], str]]:
    """
    Return Chinese character variant and text
    """
    if "／" in text:
        splite_result = text.split("／")
        if len(splite_result) != 2:
            yield None, text
        else:
            for variant_index, variant in enumerate(splite_result):
                yield "zh-Hant" if variant_index == 0 else "zh-Hans", variant
    else:
        yield None, text


def create_audio_url_dict(filename: str) -> dict[str, str]:
    # remove white space and left-to-right mark
    filename = filename.strip(" \u200e")
    file_extension = filename[filename.rfind(".") + 1 :].lower()
    if file_extension == "ogv":
        # ".ogv" pages are redirected to ".oga" pages in Wikipedia Commons
        filename = filename[: filename.rfind(".")] + ".oga"
        file_extension = "oga"
    file_url_key = file_extension + "_url"
    filename_without_prefix = filename.removeprefix("File:")
    if len(filename_without_prefix) == 0:
        return {}
    audio_dict = {
        "audio": filename_without_prefix,
        file_url_key: "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + filename_without_prefix,
    }
    transcode_formates = []
    if file_extension not in ("oga", "ogg"):
        transcode_formates.append("ogg")
    if file_extension != "mp3":
        transcode_formates.append("mp3")
    for file_suffix in transcode_formates:
        audio_dict[f"{file_suffix}_url"] = create_transcode_url(
            filename_without_prefix.replace(" ", "_"), file_suffix
        )
    return audio_dict


def create_transcode_url(filename: str, transcode_suffix: str) -> str:
    # Chinese Wiktionary template might expands filename that has the a lower
    # first letter but the actual Wikimedia Commons file's first letter is
    # capitalized
    filename = filename[0].upper() + filename[1:]
    md5 = hashlib.md5(filename.encode()).hexdigest()
    return (
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/"
        + f"{md5[0]}/{md5[:2]}/{filename}/{filename}.{transcode_suffix}"
    )


def set_sound_file_url_fields(wxr, filename, pydantic_model):
    file_data = create_audio_url_dict(filename)
    for key, value in file_data.items():
        if hasattr(pydantic_model, key):
            setattr(pydantic_model, key, value)
        else:
            wxr.wtp.warning(
                f"{key=} not defined in Sound",
                sortid="extractor.share.set_sound_file_url_fields",
            )


def split_senseids(senseids_str: str) -> list[str]:
    senseids = []
    raw_ids = (
        senseids_str.strip().removeprefix("[").removesuffix("]").split(",")
    )
    for raw_id in raw_ids:
        range_split = raw_id.split("-")
        if len(range_split) == 1:
            senseids.append(raw_id.strip())
        elif len(range_split) == 2:
            try:
                start = re.sub(r"[a-z]", "", range_split[0].strip())
                end = re.sub(r"[a-z]", "", range_split[1].strip())
                senseids.extend(
                    [
                        str(id)
                        for id in range(
                            int(start),
                            int(end) + 1,
                        )
                    ]
                )
            except Exception:
                pass

    return senseids


def calculate_bold_offsets(
    wxr,
    node: WikiNode,
    node_text: str,
    example,
    field: str,
    extra_node_kind: NodeKind | None = None,
) -> None:
    from ..page import clean_node

    offsets = []
    bold_words = set()
    for b_tag in node.find_html_recursively("b"):
        bold_words.add(clean_node(wxr, None, b_tag))
    for strong_tag in node.find_html_recursively("strong"):
        bold_words.add(clean_node(wxr, None, strong_tag))
    for bold_node in node.find_child_recursively(
        NodeKind.BOLD
        if extra_node_kind is None
        else NodeKind.BOLD | extra_node_kind
    ):
        bold_words.add(clean_node(wxr, None, bold_node))
    for link_node in node.find_child_recursively(NodeKind.LINK):
        if len(link_node.largs) > 0:
            link_dest = clean_node(wxr, None, link_node.largs[0])
            if "#" in link_dest and not link_dest.startswith("#"):
                link_dest = link_dest[:link_dest.index("#")]
            if link_dest == wxr.wtp.title:
                link_text = clean_node(wxr, None, link_node)
                bold_words.add(link_text)

    for bold_word in bold_words:
        for m in re.finditer(re.escape(bold_word), node_text):
            offsets.append((m.start(), m.end()))
    if len(offsets) > 0:
        if hasattr(example, field):  # pydantic model
            setattr(example, field, sorted(offsets))
        elif isinstance(example, dict):
            example[field] = sorted(offsets)
