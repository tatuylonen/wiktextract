import argparse
import csv
import json
import sys
from pathlib import Path

import requests


def save_json_file(data: dict[str, list[str]], lang_code: str) -> None:
    data_folder = Path(f"wiktextract/data/{lang_code}")
    if not data_folder.exists():
        data_folder.mkdir()
    with data_folder.joinpath("languages.json").open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def expand_template(sub_domain: str, text: str) -> str:
    # https://www.mediawiki.org/wiki/API:Expandtemplates
    params = {
        "action": "expandtemplates",
        "format": "json",
        "text": text,
        "prop": "wikitext",
        "formatversion": "2",
    }
    r = requests.get(f"https://{sub_domain}.wiktionary.org/w/api.php", params=params)
    data = r.json()
    return data["expandtemplates"]["wikitext"]


def parse_csv(sub_domain: str, wiki_lang_code: str) -> dict[str, list[str]]:
    # https://en.wiktionary.org/wiki/Module:list_of_languages,_csv_format
    csv_text = expand_template(
        sub_domain, "{{#invoke:list of languages, csv format|show}}"
    )
    csv_text = csv_text.removeprefix("<pre>\n").removesuffix("</pre>")

    lang_data = {}
    csv_iter = iter(csv_text.splitlines())
    next(csv_iter)  # skip header line
    for row in csv.reader(csv_iter, delimiter=";"):
        lang_code = row[1]
        canonical_name = row[2]
        other_names = list(filter(None, row[-2].split(","))) if row[-2] else []
        lang_data[lang_code] = [canonical_name] + other_names

    save_json_file(lang_data, wiki_lang_code)


def get_fr_languages():
    # https://fr.wiktionary.org/wiki/Module:langues/analyse
    json_text = expand_template(
        "fr", "{{#invoke:langues/analyse|affiche_langues_python}}"
    )
    json_text = json_text[json_text.index("{") : json_text.index("}") + 1]
    json_text = json_text.replace(",\r\n}", "}")  # remove tailing comma
    data = json.loads(json_text)
    lang_data = {}
    for lang_code, lang_name in data.items():
        lang_data[lang_code] = [lang_name[0].upper() + lang_name[1:]]

    save_json_file(lang_data, "fr")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sub_domain", help="Wiktionary sub domain")
    parser.add_argument("lang_code", help="Wiktionary language code")
    args = parser.parse_args()

    match args.lang_code:
        case "en" | "zh":
            parse_csv(args.sub_domain, args.lang_code)
        case "fr":
            get_fr_languages()


if __name__ == "__main__":
    sys.exit(main())
