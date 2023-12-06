from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Sound(BaseModelWrap):
    ipa: Optional[str] = Field(
        default=None, description="International Phonetic Alphabet"
    )
    audio: Optional[str] = Field(default=None, description="Audio file name")
    wav_url: Optional[str] = Field(default=None)
    ogg_url: Optional[str] = Field(default=None)
    oga_url: Optional[str] = Field(default=None)
    mp3_url: Optional[str] = Field(default=None)
    flac_url: Optional[str] = Field(default=None)
    tags: Optional[list[str]] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )
    homophones: Optional[list[str]] = Field(
        default=[], description="Words with same pronunciation"
    )


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="Russian Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default=None, description="Part of speech type")
    pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["ru"]
    )
    lang_name: str = Field(
        description="Localized language name of the word", examples=["Русский"]
    )
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )
    sounds: Optional[list[Sound]] = []
