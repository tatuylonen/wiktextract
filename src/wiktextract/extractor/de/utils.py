import re
from typing import List

from wikitextprocessor import NodeKind, WikiNode


def match_senseid(node_text: str):
    match = re.match(r"\[(\d*[a-z]?)\]", node_text)

    if match:
        senseid = match.group(1)
        node_text = node_text[match.end() :].strip()
    else:
        senseid = None

    return senseid, node_text


def find_and_remove_child(node: WikiNode, kind: NodeKind, cb=None):
    children = []
    for idx, child in reversed(list(node.find_child(kind, with_index=True))):
        if cb and not cb(child):
            continue
        del node.children[idx]
        children.append(child)
    return reversed(children)


def split_senseids(senseids_str: str) -> List[str]:
    senseids = []
    raw_ids = (
        senseids_str.strip().removeprefix("[").removesuffix("]").split(",")
    )
    for raw_id in raw_ids:
        range_split = raw_id.split("-")
        if len(range_split) == 1:
            senseids.append(raw_id.strip())
        elif len(range_split) == 2:
            try:
                start = re.sub(r"[a-z]", "", range_split[0].strip())
                end = re.sub(r"[a-z]", "", range_split[1].strip())
                senseids.extend(
                    [
                        str(id)
                        for id in range(
                            int(start),
                            int(end) + 1,
                        )
                    ]
                )
            except:
                pass

    return senseids
