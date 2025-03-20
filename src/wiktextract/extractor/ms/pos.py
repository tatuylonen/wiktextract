from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import Form, Sense, WordEntry
from .section_titles import POS_DATA


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    gloss_list_index = len(level_node.children)
    for index, node in enumerate(level_node.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#") and node.sarg.endswith("#"):
                    extract_gloss_list_item(wxr, page_data[-1], list_item)
                    if index < gloss_list_index:
                        gloss_list_index = index
        elif isinstance(node, TemplateNode) and (
            node.template_name.endswith(
                (
                    "-ks",
                    "-adj",
                    "-kn",
                    "-noun",
                    "-kk",
                    "-verb",
                    "-kerja",
                    "-kgn",
                    "-pron",
                    "-kkt",
                    "-adv",
                    "-kp",
                    "-sendi",
                    "-prep",
                    "-seru",
                    "-kanji",
                    "-hanzi",
                    "-hanja",
                    "-conj",
                    "-hantu",
                )
            )
            or node.template_name in ["inti", "head", "Han char"]
        ):
            extract_pos_header_template(wxr, page_data, base_data, node)

    if len(page_data[-1].senses) == 0:
        page_data.pop()


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
) -> None:
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in [
                "label",
                "lb",
                "konteks",
                "context",
                "konteks 1",
                "context 2",
            ]:
                extract_label_template(wxr, sense, node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)
    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
    if len(sense.glosses) > 0:
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)
        elif child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for e_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, word_entry, sense, e_list_item)


def extract_pos_header_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    t_node: TemplateNode,
) -> None:
    cats = {}
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_template.find_child(NodeKind.LINK):
        clean_node(wxr, cats, link_node)
    pos_type = "unknown"
    pos_tags = []
    for cat in cats.get("categories", []):
        for pos_title, pos_data in POS_DATA.items():
            if cat.startswith(pos_title):
                pos_type = pos_data["pos"]
                pos_tags = pos_data.get("tags", [])
                break
        if pos_type != "unknown":
            break
    if page_data[-1].pos_title == "Takrifan" and page_data[-1].pos != "unknown":
        page_data.append(base_data.model_copy(deep=True))
        page_data[-1].pos = pos_type
        page_data[-1].pos_title = "Takrifan"
        page_data[-1].tags.extend(pos_tags)
    if page_data[-1].pos == "unknown":
        page_data[-1].pos = pos_type
        page_data[-1].tags.extend(pos_tags)
    page_data[-1].categories.extend(cats.get("categories", []))

    raw_tag = ""
    for node in expanded_template.find_child_recursively(NodeKind.HTML):
        match node.tag:
            case "i":
                raw_tag = clean_node(wxr, None, node)
            case "b":
                form = Form(form=clean_node(wxr, None, node))
                if raw_tag != "":
                    form.raw_tags.append(raw_tag)
                if form.form != "":
                    page_data[-1].forms.append(form)


def extract_label_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    text = clean_node(wxr, sense, t_node).strip("() ")
    for raw_tag in text.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)
