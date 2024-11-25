import importlib
import json
from pathlib import Path
from importlib.resources import files


def main() -> None:
    """
    Run this script at the project root folder to generate JSON schema files of
    each extractor that has pydantic model `WordEntry` defined in the
    `models.py` file.
    """

    extractor_folder = files("wiktextract") / "extractor"
    output_path = Path("_site")
    output_path.mkdir(exist_ok=True)
    for extractor_folder in filter(
        lambda p: p.is_dir()
        and p.stem != "template"
        and (p / "models.py").is_file(),
        (files("wiktextract") / "extractor").iterdir(),
    ):
        lang_code = extractor_folder.stem
        model_module = importlib.import_module(
            f"wiktextract.extractor.{lang_code}.models"
        )
        model_schema = model_module.WordEntry.model_json_schema()
        model_schema["$id"] = f"https://kaikki.org/{lang_code}.json"
        model_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if "description" in model_schema:
            model_schema["description"] = model_schema["description"].replace(
                "\n", " "
            )
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


if __name__ == "__main__":
    main()
