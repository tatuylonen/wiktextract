import re

from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry

JA_KANJI_TEMPLATE_PARAMS = {
    "呉音": "go-on",
    "漢音": "kan-on",
    "唐音": "to-on",
    "慣用音": "kan-yo-on",
    "音": "on",
    "訓": "kun",
    "古訓": "ko-kun",
    "名乗り": "nanori",
}
"""Parameters of the ja-kanji template that contain readings.

On'yomi (音読み); Chinese-derived readings (katakana):
- 呉音 (go-on): Historical reading
- 漢音 (kan-on): Historical reading
- 唐音 (to-on): Historical reading
- 慣用音 (kan-yo-on): Customary reading, often corrupted or non-standard
- 音 (on): Generic on'yomi when the specific type is unknown

Kun'yomi (訓読み); native Japanese readings (hiragana):
- 訓 (kun): Standard kun'yomi
- 古訓 (ko-kun): Archaic kun'yomi
- 名乗り (nanori): Readings used exclusively in personal names
"""


def _parse_readings(raw: str) -> list[str]:
    return [
        r
        for raw_r in raw.split(",")
        if (r := re.sub(r"[<;/].*$", "", raw_r).strip())
    ]


def extract_ja_kanji(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
) -> None:
    # https://ja.wiktionary.org/wiki/テンプレート:ja-kanji
    # First collect 常用 (joyo) readings (readings in active use)
    # it mixes on'yomi (katakana) and kun'yomi (hiragana)
    #
    # We can find 呉音=*, meaning the reading is the same as the kan-on 漢音
    joyo = set()
    joyo_value = t_node.template_parameters.get("常用", "")
    if joyo_value:
        joyo_reading = clean_node(wxr, base_data, joyo_value)
        for r in _parse_readings(joyo_reading):
            joyo.add(r)

    # Collect kan-on readings first so 呉音=* can reference them
    # (we can't repeat the previous logic due to numbering: 漢音1=, 漢音2=)
    kan_on_readings: list[str] = []
    for param, value in t_node.template_parameters.items():
        if not isinstance(param, str):
            continue
        base_param = re.sub(r"\d+$", "", param)
        reading_type = JA_KANJI_TEMPLATE_PARAMS.get(base_param)
        if reading_type == "kan-on":
            raw = clean_node(wxr, base_data, value)
            for r in _parse_readings(raw):
                kan_on_readings.append(r)

    # Then extract the remaining readings to append them, tagging joyo ones
    # accordingly and resolving if necessary.
    for param, value in t_node.template_parameters.items():
        if not isinstance(param, str):
            continue
        base_param = re.sub(r"\d+$", "", param)
        reading_type = JA_KANJI_TEMPLATE_PARAMS.get(base_param)
        if reading_type is None:
            continue
        raw = clean_node(wxr, base_data, value)
        readings = (
            kan_on_readings
            if (reading_type == "go-on" and raw.strip() == "*")
            else _parse_readings(raw)
        )
        for r in readings:
            tags = [reading_type]
            if r in joyo:
                tags.append("joyo")
            base_data.forms.append(
                Form(form=r, tags=["transliteration", *tags])
            )
