import re


def ka_decl_noun_template_cell(alts: list[str]) -> list[tuple[str, str, str]]:
    nalts = []
    for alt in alts:
        orig, roman = re.split(r" \(", alt, maxsplit=1)
        orig = orig.strip()
        roman = roman.strip().removesuffix(")")
        if "(" not in orig:
            nalts.append((orig, roman, ""))
        else:
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
