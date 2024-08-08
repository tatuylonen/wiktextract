"""Handle specific templates, starting with `Template:+obj`.
Each template should have a properly annotated function
associated with its name in info_templates, and it should
handle the given node based on where it is called from
(`location`), like head or sense.
"""

import re
from typing import Callable, Optional, Union

from wikitextprocessor import WikiNode
from wikitextprocessor.core import TemplateArgs
from wikitextprocessor.parser import TemplateNode
from wiktextract.clean import clean_template_args, clean_value
from wiktextract.form_descriptions import decode_tags
from wiktextract.type_utils import PlusObjTemplateData, TemplateData
from wiktextract.wxr_context import WiktextractContext

InfoNode = Union[str, WikiNode]

InfoReturnTuple = tuple[
    Optional[TemplateData],  # template data field contents or None
    Optional[Union[str, WikiNode]],  # template output or None if it should
    # not be expressed (like `+obj` in heads). Return the original
    # WikiNode if nothing special needs to happen.
]


InfoTemplateFunc = Callable[
    [
        WiktextractContext,
        InfoNode,  # the node being checked
        str,  # location from where this is called
    ],
    InfoReturnTuple,
]

PLUSOBJ_RE = re.compile(r"\[with ([^][=]+)( = ([^][]+))?\]")


def plusobj_func(
    wxr: WiktextractContext, node: InfoNode, loc: str
) -> InfoReturnTuple:
    """Parse the output of Template:+obj,
    `[+infinitive or ergative = meaning]`"""

    if not isinstance(node, TemplateNode):
        wxr.wtp.error(
            "plusobj_func: node is note a TemplateNode",
            sortid="info_templates/45",
        )
        return None, None

    text = clean_value(wxr, wxr.wtp.expand(wxr.wtp.node_to_wikitext(node)))
    # print(f"cleaned: {text=}")
    m = PLUSOBJ_RE.search(text)
    if not m:
        wxr.wtp.error(
            f"INFO-TEMPLATES: `Template:+obj` expansion does not "
            f"match regex: {text}",
            sortid="info_templates: 78",
        )
        return None, None
    taggers = m.group(1)
    meaning = m.group(3)

    extra_data: PlusObjTemplateData = {"words": [], "tags": []}
    if meaning:
        extra_data["meaning"] = meaning

    for ortags in re.split(r",| or ", taggers):
        tagsets, _ = decode_tags(ortags)
        for tagset in tagsets:
            if "error-unknown-tag" in tagset:
                extra_data["words"].extend(ortags.split())
            else:
                extra_data["tags"].extend(tagset)
    if not extra_data["words"]:
        del extra_data["words"]
    if not extra_data["tags"]:
        del extra_data["tags"]
    else:
        extra_data["tags"] = sorted(set(extra_data["tags"]))

    ret_template_data: TemplateData = {
        "args": clean_template_args(wxr, node.template_parameters),
        "name": "+obj",
        "extra_data": extra_data,
        "expansion": text,
    }

    if loc == "head":
        return ret_template_data, None

    # if "sense", keep text in sense
    return ret_template_data, text


INFO_TEMPLATE_FUNCS: dict[str, InfoTemplateFunc] = {
    "+obj": plusobj_func,
}


def parse_info_template_node(
    wxr: WiktextractContext, node: Union[str, WikiNode], loc: str
) -> InfoReturnTuple:
    if not isinstance(node, WikiNode):
        return None, None
    if (
        not isinstance(node, TemplateNode)
        or node.template_name not in INFO_TEMPLATE_FUNCS
    ):
        return None, None

    return INFO_TEMPLATE_FUNCS[node.template_name](wxr, node, loc)


def parse_info_template_arguments(
    wxr: WiktextractContext, name: str, args: TemplateArgs, loc: str
) -> InfoReturnTuple:
    templ_s = "{{" + name
    zipped = [(str(k), v) for k, v in args.items()]
    for k, v in sorted(zipped):
        if k.isnumeric():
            templ_s += f"|{v}"
        else:
            templ_s += f"|{k}={v}"
    templ_s += "}}"
    templ_node = wxr.wtp.parse(templ_s)
    if len(templ_node.children) > 0:
        tnode = wxr.wtp.parse(templ_s).children[0]
        if not isinstance(tnode, WikiNode):
            return None, None
        templ_node = tnode
    else:
        return None, None

    return parse_info_template_node(
        wxr,
        templ_node,
        "sense",
    )
