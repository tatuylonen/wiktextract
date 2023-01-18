import argparse
import csv
import json
import sys
from pathlib import Path


def save_json_file(data: dict[str, list[str]],
                   lang_code: str,
                   file_name: str = "languages.json") -> None:
    data_folder = Path(f"wiktextract/data/{lang_code}")
    if not data_folder.exists():
        data_folder.mkdir()
    with data_folder.joinpath(file_name).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def expand_template(sub_domain: str, text: str) -> str:
    import requests

    # https://www.mediawiki.org/wiki/API:Expandtemplates
    params = {
        "action": "expandtemplates",
        "format": "json",
        "text": text,
        "prop": "wikitext",
        "formatversion": "2",
    }
    r = requests.get(f"https://{sub_domain}.wiktionary.org/w/api.php",
                     params=params)
    data = r.json()
    return data["expandtemplates"]["wikitext"]

def get_source_code(sub_domain: str, page: str) -> str:
    # Sometimes, like for Czech, the templates cannot be expanded, so we have to parse the source code
    import requests

    # https://www.mediawiki.org/wiki/API:Parse
    params = {
        "action": "parse",
        "format": "json",
        "page": page,
        "prop": "wikitext",
        "formatversion": "2",
    }
    r = requests.get(f"https://{sub_domain}.wiktionary.org/w/api.php",
                     params=params)
    data = r.json()
    return data["parse"]["wikitext"]


def add_simplified_chinese_names(lang_names, converter):
    # The API only returns language names in Traditional Chinese characters
    for name in lang_names.copy():
        simplified_name = converter.convert(name)
        if simplified_name not in lang_names:
            lang_names.append(simplified_name)


def parse_csv(sub_domain: str, wiki_lang_code: str) -> dict[str, list[str]]:
    # https://en.wiktionary.org/wiki/Module:list_of_languages,_csv_format
    csv_text = expand_template(
        sub_domain, "{{#invoke:list of languages, csv format|show}}"
    )
    csv_text = csv_text.removeprefix("<pre>\n").removesuffix("</pre>")

    if wiki_lang_code == "zh":
        import opencc

        converter = opencc.OpenCC("t2s.json")
    lang_data = {}
    csv_iter = iter(csv_text.splitlines())
    next(csv_iter)  # skip header line
    for row in csv.reader(csv_iter, delimiter=";"):
        lang_code = row[1]
        canonical_name = row[2]
        other_names = list(filter(None, row[-2].split(","))) if row[-2] else []
        all_names = [canonical_name] + other_names
        if wiki_lang_code == "zh":
            add_simplified_chinese_names(all_names, converter)
        lang_data[lang_code] = all_names

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


def get_languages_cs_sk(wk_lang_code: str):
    # https://cs.wiktionary.org/wiki/Modul:Languages
    source_code = get_source_code(wk_lang_code, "Modul:Languages")
    source_code = source_code[source_code.index("--]]") + 4:]
    source_code = source_code.replace("Languages = ", "", 1)
    source_code = source_code[:source_code.rindex("}") + 1]

    lang_data = {}
    for line in source_code.splitlines():
        line = line.strip()
        if line.startswith("["):
            lang_code = line[1:line.index("]")]
            lang_code = lang_code.replace('\"', '')
            lang_data[lang_code] = []
        elif line.startswith("name = "):
            lang_name = line[7:line.index(",")]

            lang_name = lang_name.replace('\"', '')
            lang_data[lang_code].append(lang_name)

    lang_data = {k: v for k, v in lang_data.items() if v != [] and v != ["—"]}
    
    save_json_file(lang_data, wk_lang_code)
    

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
        case "cs" | "sk":
            get_languages_cs_sk(args.lang_code)


if __name__ == "__main__":
    sys.exit(main())
