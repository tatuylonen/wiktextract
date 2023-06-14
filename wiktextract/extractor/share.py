from typing import List, Union

from wikitextprocessor import WikiNode, NodeKind


WIKIMEDIA_COMMONS_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/"


def contains_list(
    contents: Union[WikiNode, List[Union[WikiNode, str]]]
) -> bool:
    """Returns True if there is a list somewhere nested in contents."""
    if isinstance(contents, (list, tuple)):
        return any(contains_list(x) for x in contents)
    if not isinstance(contents, WikiNode):
        return False
    kind = contents.kind
    if kind == NodeKind.LIST:
        return True
    return contains_list(contents.children) or contains_list(contents.args)
