from wikitextprocessor import NodeKind, WikiNode
from wiktextract.extractor.es.models import EtymologyTemplate, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def process_etymology_block(
    wxr: WiktextractContext,
    entry: WordEntry,
    level_node: WikiNode,
):
    """
    https://es.wiktionary.org/wiki/Plantilla:etimología
    https://es.wiktionary.org/wiki/Plantilla:etimología2

    When the etymology templates have no arguments that means this word has
    no etymology info yet.

    If they only have the "leng" (language) param, that means there's no info
    and this word is from a language other than Spanish.

    When there's no info, "etymology_text" should be missing.
    """

    has_etymology_info = False
    for template_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        entry.etymology_templates = entry.etymology_templates or []

        etymology_template = EtymologyTemplate(
            name=template_node.template_name,
            expansion=clean_node(wxr, None, template_node),
        )

        args = {}
        for index, param in template_node.template_parameters.items():
            args[str(index)] = (
                param
                if isinstance(param, str)
                else clean_node(wxr, None, param)
            )
            has_etymology_info = has_etymology_info or index != "leng"
        if args:
            etymology_template.args = args

        entry.etymology_templates.append(etymology_template)

    if has_etymology_info:
        entry.etymology_text = clean_node(wxr, None, level_node.children)
