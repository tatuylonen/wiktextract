from typing import Dict, List

from wikitextprocessor import WikiNode
from wiktextract.datautils import data_append
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


GENDERS = {"f": "feminine", "m": "masculine", "n": "neuter"}


FORM_TAGS = {
    "複數": ["plural"],
    "第三人稱單數簡單現在時": ["third-person", "singular", "simple", "present"],
    "現在分詞": ["present", "participle"],
    "一般過去時及過去分詞": ["past", "participle"],
    "指小詞": ["diminutive"],
}


def extract_headword_line(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
    lang_code: str,
) -> None:
    template_name = node.args[0][0]
    if template_name == "head" or template_name.startswith(f"{lang_code}-"):
        if lang_code == "ja":
            pass
        else:
            extract_common_headword(wxr, page_data, node)


def extract_common_headword(
    wxr: WiktextractContext, page_data: List[Dict], node: WikiNode
) -> None:
    expanded_text = clean_node(wxr, None, node)
    headword_text = expanded_text.removeprefix(wxr.wtp.title).strip()
    first_parenthesis_index = headword_text.find("(")
    if first_parenthesis_index != "-1":
        gender_text = headword_text[:first_parenthesis_index].strip()
        if gender_type := GENDERS.get(gender_text):
            data_append(wxr, page_data[-1], "tags", gender_type)
        for split_text in headword_text[first_parenthesis_index + 1 : -1].split(
            "，"
        ):
            if split_text.endswith("可數"):
                for countable_text in split_text.split("&"):
                    countable_text = countable_text.strip()
                    countable_type = None
                    if countable_text.endswith("不可數"):
                        # "不可数" or "通常不可数"
                        countable_type = "uncountable"
                    elif countable_text == "可數":
                        countable_type = "countable"
                    data_append(wxr, page_data[-1], "tags", countable_type)
            elif " " in split_text:
                form_type_text, forms_text = split_text.split(maxsplit=1)
                if form_type_text in FORM_TAGS:
                    for form in forms_text.split("或"):
                        gender_suffixes = tuple(
                            f" {gender}" for gender in GENDERS.keys()
                        )
                        tags = FORM_TAGS[form_type_text]
                        if form.endswith(gender_suffixes):
                            form, gender_text = form.rsplit(maxsplit=1)
                            tags.append(GENDERS[gender_text])
                        data_append(
                            wxr,
                            page_data[-1],
                            "forms",
                            {
                                "form": form.strip(),
                                "tags": tags,
                            },
                        )
