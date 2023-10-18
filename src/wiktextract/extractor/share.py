import hashlib
import re
from html import unescape
from typing import Dict, Iterable, List, Optional, Tuple, Union

from wikitextprocessor import WikiNode


def strip_nodes(
    nodes: List[Union[WikiNode, str]]
) -> Iterable[Union[WikiNode, str]]:
    # filter nodes that only have newlines, white spaces and non-breaking spaces
    return filter(
        lambda node: isinstance(node, WikiNode)
        or (isinstance(node, str) and len(unescape(node).strip()) > 0),
        nodes,
    )


def capture_text_in_parentheses(text: str) -> Tuple[List[str], str]:
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
        capture_text_list.append(m.group()[1:-1])

    rest_text = " ".join(rest_parts) if len(rest_parts) > 0 else text
    return capture_text_list, rest_text


def split_chinese_variants(text: str) -> Iterable[Tuple[Optional[str], str]]:
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


def create_audio_url_dict(filename: str) -> Dict[str, str]:
    file_url_key = filename[filename.rfind(".") + 1 :].lower() + "_url"
    filename_without_prefix = filename.removeprefix("File:")
    audio_dict = {
        "audio": filename_without_prefix,
        file_url_key: "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + filename_without_prefix,
    }
    transcode_formates = []
    if not filename.lower().endswith((".oga", ".ogg")):
        transcode_formates.append("ogg")
    if not filename.lower().endswith(".mp3"):
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


def split_tag_text(text: str) -> List[str]:
    """
    Find tags enclosded in parentheses and remove parentheses
    """
    return [
        tag.strip("()").strip()
        for tag in re.split(r"(?<=\))\s+(?=\()", text.strip())
    ]
