from typing import cast

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import TemplateData, WordEntry


def process_etymology_block(
    wxr: WiktextractContext,
    entry: WordEntry,
    level_node: WikiNode,
) -> None:
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
        # no-op type-annotation cast; we softly assert template_node is a
        # TemplateNode, which has .template_name, to quiet the type-checker.
        template_node = cast(TemplateNode, template_node)
        if "etim" not in template_node.template_name:
            # We don't want to keep any other template data other than
            # the main etymology templates (and maybe Plantilla:etim)
            continue

        entry.etymology_templates = entry.etymology_templates or []

        etymology_template = TemplateData(
            name=template_node.template_name,
            expansion=clean_node(wxr, None, template_node),
        )

        if etymology_template.expansion in (
            # "Please fill in this etymology, thank you..."
            "Si puedes, incorpórala: ver cómo.",
            "Préstamo no adaptado.",
            "Este lema en este idioma es ampliable. "
            "Retira este aviso si la mayor parte de las acepciones ya están incluidas.",
        ):
            continue

        args = {}
        for index, param in template_node.template_parameters.items():
            args[str(index)] = (
                param
                if isinstance(param, str)
                else clean_node(wxr, None, param)
            )
            # if any other index other than "leng" is encountered,
            # has_etymology => True
            has_etymology_info = has_etymology_info or index != "leng"
        if args and not (len(args) == 1 and "leng" in args):
            etymology_template.args = args

        entry.etymology_templates.append(etymology_template)

    if has_etymology_info:
        entry.etymology_text = clean_node(
            wxr, None, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
        )
