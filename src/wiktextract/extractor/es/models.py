from typing import Optional
import json

import logging

from pydantic import BaseModel, Field, model_validator, ValidationError
from pydantic.json_schema import GenerateJsonSchema

from wiktextract.wxr_context import WiktextractContext


class PydanticLogger:
    wxr: Optional[WiktextractContext] = None

    @classmethod
    def debug(
        cls, msg: str, trace: Optional[str] = None, sortid: str = "XYZunsorted"
    ):
        if cls.wxr:
            cls.wxr.wtp.debug(msg, trace=trace, sortid=sortid)
        else:
            logging.debug(msg)


class BaseModelWrap(BaseModel):
    class Config:
        extra = "ignore"
        validate_assignment = True

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)
        return self

    def get(self, key: str, _=None):
        return getattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        try:
            setattr(self, item, value)
        except ValidationError:
            pass


class LoggingExtraFieldsModel(BaseModelWrap):
    @model_validator(mode="before")
    def log_extra_fields(cls, values):
        all_allowed_field_names = {key for key in cls.__fields__.keys()}
        extra_fields = {
            name: str(value)
            for name, value in values.items()
            if name not in all_allowed_field_names
        }
        if extra_fields:
            class_full_name = cls.__name__
            PydanticLogger.debug(
                msg=f"Pydantic - Got extra fields in {class_full_name}: {extra_fields}",
                sortid="wiktextract/extractor/es/pydantic/extra_fields/33",
            )
        return values


class Sense(LoggingExtraFieldsModel):
    glosses: list[str] = Field(
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging."
    )
    tags: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging.",
    )
    categories: list[str] = Field(
        default=[],
        description="list of sense-disambiguated category names extracted from (a subset) of the Category links on the page",
    )
    # examples: list[SenseExample] = []
    subsenses: list["Sense"] = Field(
        default=[], description="List of subsenses"
    )
    senseid: Optional[int] = Field(
        default=None, description="Sense number used in Wiktionary"
    )


class WordEntry(LoggingExtraFieldsModel):
    """WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract."""

    word: str = Field(description="word string")
    pos: str = Field(default=None, description="Part of speech type")
    pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["es"]
    )
    lang_name: str = Field(
        description="Localized language name of the word", examples=["español"]
    )
    senses: Optional[list[Sense]] = []
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )


if __name__ == "__main__":

    class JsonSchemaGenerator(GenerateJsonSchema):
        def generate(self, schema, mode="validation"):
            json_schema = super().generate(schema, mode=mode)
            json_schema["title"] = "Spanish Wiktionary"
            json_schema["$id"] = "https://kaikki.org/es.json"
            json_schema["$schema"] = self.schema_dialect
            return json_schema

    with open("json_schema/es.json", "w") as f:
        json.dump(
            WordEntry.model_json_schema(schema_generator=JsonSchemaGenerator),
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
