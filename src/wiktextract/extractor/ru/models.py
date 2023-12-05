import json

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import GenerateJsonSchema


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class WordEntry(BaseModelWrap):
    """WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract."""

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


if __name__ == "__main__":

    class JsonSchemaGenerator(GenerateJsonSchema):
        def generate(self, schema, mode="validation"):
            json_schema = super().generate(schema, mode=mode)
            json_schema["title"] = "Russian Wiktionary"
            json_schema["$id"] = "https://kaikki.org/ru.json"
            json_schema["$schema"] = self.schema_dialect
            return json_schema

    with open("json_schema/ru.json", "w") as f:
        json.dump(
            WordEntry.model_json_schema(schema_generator=JsonSchemaGenerator),
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
