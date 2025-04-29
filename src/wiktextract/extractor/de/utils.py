import re


def extract_sense_index(node_text: str) -> tuple[str, str]:
    # [1], [1-2], [1, 2], [1.1], [1a]
    match = re.match(r"\[[\d\sa-z,.\-–?]*\]", node_text)
    if match is not None:
        sense_idx = match.group(0).replace("?", "").strip("[] ")
        node_text = node_text[match.end() :].strip()
    else:
        sense_idx = ""

    return sense_idx, re.sub(r"^[,—]*\s*", "", node_text.strip())
