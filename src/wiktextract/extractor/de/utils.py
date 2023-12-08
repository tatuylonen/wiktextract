import re

from wikitextprocessor import NodeKind, WikiNode


def match_senseid(node_text: str):
    match = re.match(r"\[(\d*(?:[a-z]|(?:\.\d+))?)\]", node_text)

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
