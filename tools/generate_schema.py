import importlib
import json
from importlib.resources import files
from pathlib import Path


def iter_schemas():
    extractor_folder = files("wiktextract") / "extractor"
    for extractor_folder in filter(
        lambda p: p.is_dir()
        and p.stem not in ["template", "sv"]
        and (p / "models.py").is_file(),
        (files("wiktextract") / "extractor").iterdir(),
    ):
        lang_code = extractor_folder.stem
        model_module = importlib.import_module(
            f"wiktextract.extractor.{lang_code}.models"
        )
        model_schema = model_module.WordEntry.model_json_schema(
            mode="serialization"
        )
        model_schema["$id"] = f"https://kaikki.org/{lang_code}.json"
        model_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if "description" in model_schema:
            model_schema["description"] = model_schema["description"].replace(
                "\n", " "
            )
        yield lang_code, model_schema


def create_json_schema_files():
    """
    Run this script at the project root folder to generate JSON schema files of
    each extractor that has pydantic model `WordEntry` defined in the
    `models.py` file.
    """
    output_path = Path("_site")
    output_path.mkdir(exist_ok=True)
    for lang_code, model_schema in iter_schemas():
        with (output_path / f"{lang_code}.json").open(
            "w", encoding="utf-8"
        ) as f:
            json.dump(
                model_schema,
                f,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
