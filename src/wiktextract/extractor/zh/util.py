from typing import Any

from .models import WordEntry


def append_base_data(
    page_data: list[WordEntry], field: str, value: Any, base_data: WordEntry
) -> None:
    """
    Chinese Wiktionary's POS sections could under other sections or at the same
    level of other sections. This function is to decide whether append a new
    WordEntry data.
    """
    if len(page_data) == 0 or (
        len(getattr(page_data[-1], field)) > 0 and len(page_data[-1].senses) > 0
    ):
        # Append new entry if last data has same field and also has gloss data
        page_data.append(base_data.model_copy(deep=True))

    # Don't append new WordEntry if POS section is not processed
    # Example page "kirin", "北庫爾德語" section
    pre_data = getattr(page_data[-1], field)
    if isinstance(pre_data, list):
        pre_data.append(value)
    else:
        setattr(page_data[-1], field, value)
