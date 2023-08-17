import hashlib
import re
from typing import Dict, List, Optional, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.datautils import append_base_data
from wiktextract.extractor.share import WIKIMEDIA_COMMONS_URL, contains_list
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_pronunciation_recursively(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    lang_code: str,
    node: Union[WikiNode, List[Union[WikiNode, str]]],
    tags: List[str],
) -> None:
    if isinstance(node, list):
        for x in node:
            extract_pronunciation_recursively(
                wxr, page_data, base_data, lang_code, x, tags
            )
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind == NodeKind.LIST_ITEM:
        if not contains_list(node):
            used_children = node.children
            rest_children = []
        else:
            used_children = [
                child
                for child in node.children
                if not isinstance(child, WikiNode)
                or child.kind != NodeKind.LIST
            ]
            rest_children = [
                child
                for child in node.children
                if isinstance(child, WikiNode) and child.kind == NodeKind.LIST
            ]
        data = extract_pronunciation_item(wxr, lang_code, used_children, tags)
        if isinstance(data, str):  # is audio file name
            # audio file usually after Pinyin
            # add back to previous Pinyin dictionary if it doesn't have
            # audio file data and they are sibling nodes(similar tags).
            last_sounds_list = page_data[-1].get("sounds", [])
            for index in range(len(last_sounds_list)):
                if last_sounds_list[index].get("audio") is None and (
                    tags == last_sounds_list[index].get("tags", [])[:-1]
                    or lang_code != "zh"
                ):
                    page_data[-1].get("sounds")[index].update(
                        create_audio_url_dict(data)
                    )
        elif isinstance(data, dict):
            append_base_data(
                page_data,
                "sounds",
                [data],
                base_data,
            )
            # list children could contain audio file
            extract_pronunciation_recursively(
                wxr,
                page_data,
                base_data,
                lang_code,
                rest_children,
                data.get("tags")[:-1],
            )
        elif isinstance(data, list):
            # list item is a tag
            extract_pronunciation_recursively(
                wxr,
                page_data,
                base_data,
                lang_code,
                rest_children,
                data,
            )
    else:
        extract_pronunciation_recursively(
            wxr, page_data, base_data, lang_code, node.children, tags
        )


def create_audio_url_dict(filename: str) -> Dict[str, str]:
    file_url_key = (
        "ogg_url"
        if filename.endswith(".ogg")
        else filename[filename.rfind(".") + 1 :].lower() + "_url"
    )
    filename_without_prefix = filename.removeprefix("File:")
    audio_dict = {
        "audio": filename_without_prefix,
        file_url_key: WIKIMEDIA_COMMONS_URL + filename,
    }
    for file_suffix in ["ogg", "mp3"]:
        transcode_url_key = f"{file_suffix}_url"
        if file_url_key != transcode_url_key:
            audio_dict[transcode_url_key] = create_transcode_url(
                filename_without_prefix, file_suffix
            )
    return audio_dict


def create_transcode_url(filename: str, transcode_suffix) -> str:
    # Chinese Wiktionary template might expands filename that has the a lower
    # first letter but the actual Wikimedia Commons file's first letter is
    # capitalized
    filename = filename[0].upper() + filename[1:]
    filename = filename.replace(" ", "_")
    md5 = hashlib.md5(filename.encode()).hexdigest()
    return (
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/"
        + f"{md5[0]}/{md5[:2]}/{filename}/{filename}.{transcode_suffix}"
    )


def combine_pronunciation_tags(
    old_tags: List[str], new_tags: List[str]
) -> List[str]:
    combined_tags = old_tags[:]
    old_tags_set = set(old_tags)
    for tag in new_tags:
        if tag not in old_tags_set:
            combined_tags.append(tag)
    return combined_tags


def split_pronunciation_tags(text: str) -> List[str]:
    return list(
        filter(
            None,
            re.split(
                r"，|, | \(|\) ?|和|包括|: |、",
                text.removesuffix("^((幫助))")  # remove help link
                # remove link to page "Wiktionary:漢語發音表記"
                .removesuffix("(維基詞典)").strip("（）()⁺\n "),
            ),
        )
    )


def extract_pronunciation_item(
    wxr: WiktextractContext,
    lang_code: str,
    node_children: List[WikiNode],
    tags: List[str],
) -> Optional[Union[Dict, str, List[str]]]:
    """
    Return audio file name(eg. "File:LL-Q1860 (eng)-Vealhurl-manga.wav") string
    or a dictionary contains IPA and tags
    or a list of tags
    """
    expanded_text = clean_node(wxr, None, node_children)
    # remove Dungan language pronunciation warning from "Module:Zh-pron"
    expanded_text = expanded_text.removesuffix(
        "(注意：東干語發音目前仍處於實驗階段，可能會不準確。)"
    )

    if expanded_text.startswith("File:"):
        return expanded_text
    elif expanded_text.startswith("(福建: "):
        # it's a tag
        return combine_pronunciation_tags(
            tags, split_pronunciation_tags(expanded_text)
        )
    else:
        sound_tags_text, *ipa = re.split(r"：|:", expanded_text, 1)
        new_tags = combine_pronunciation_tags(
            tags, split_pronunciation_tags(sound_tags_text)
        )
        if len(ipa) > 0:
            data = {"tags": new_tags}
            ipa_key = "zh-pron" if lang_code == "zh" else "ipa"
            data[ipa_key] = ipa[0].strip()
            return data

        for child in filter(
            lambda x: isinstance(x, WikiNode) and x.kind == NodeKind.TEMPLATE,
            node_children,
        ):
            template_name, *template_args = child.largs
            if template_name[0] == "audio":
                audio_filename = template_args[1][0]
                return audio_filename

        return new_tags
