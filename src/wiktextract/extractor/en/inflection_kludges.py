import re


def ka_decl_noun_template_cell(alts: list[str]) -> list[tuple[str, str, str]]:
    orig, roman = re.split(r" \(", alts[0], maxsplit=1)
    orig = orig.strip()
    roman = roman.strip().removesuffix(")")
    if "(" not in orig:
        nalts = [(orig, roman, "")]
    else:
        nalts = []
        nalts.append(
            (
                re.sub(r"\(.*?\)", "", orig),
                re.sub(r"\(.*?\)", "", roman),
                "",
            )
        )
        nalts.append(
            (
                re.sub(r"\(|\)", "", orig),
                re.sub(r"\(|\)", "", roman),
                "",
            )
        )
    return nalts
