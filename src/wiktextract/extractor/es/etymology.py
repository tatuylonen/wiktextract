from wikitextprocessor import NodeKind, WikiNode
from wiktextract.extractor.es.models import EtymologyTemplate, WordEntry
from wiktextract.page import clean_node, LEVEL_KINDS
from wiktextract.wxr_context import WiktextractContext


IGNORED_NODE_LEVELS = [NodeKind.HTML] + list(LEVEL_KINDS)

SKIPPED_TEMPLATES = (
    "ampliable",
    "arcoiris",
    "clear",
    "cita requerida",
)


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
    ignore_these_templates: list[WikiNode] = []
    for ignored_node in level_node.find_child_recursively(IGNORED_NODE_LEVELS):
        # stuff inside <ref></ref> should be ignored, and obvious mistakes
        # like a sub-section to etymology (wrong level kind, in es.wiktionary
        # these should all apparently be sibligns, so Etymology sections
        # shouldn't have other levels as their children (example:
        # calzado around 2024-01-30
        if ignored_node.kind == NodeKind.HTML and ignored_node.sarg == "reg":
            # HTML nodes other than REG should be fine
            continue
        ignore_these_templates.extend(
            ignored_node.find_child_recursively(NodeKind.TEMPLATE)
        )

    for template_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if template_node in ignore_these_templates:
            continue

        if template_node.template_name in SKIPPED_TEMPLATES:
            continue

        entry.etymology_templates = entry.etymology_templates or []

        etymology_template = EtymologyTemplate(
            name=template_node.template_name,
            expansion=clean_node(wxr, None, template_node),
        )

        if etymology_template.expansion in (
            # "Please fill in this etymology, thank you..."
            "Si puedes, incorpórala: ver cómo",
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
            has_etymology_info = has_etymology_info or index != "leng"
        if args:
            etymology_template.args = args

        # DEBUG
        if not args:
            print(f"EMPTY ARGS in {entry.word}, {etymology_template}")

        entry.etymology_templates.append(etymology_template)

    if has_etymology_info:
        entry.etymology_text = clean_node(wxr, None, level_node.children)
