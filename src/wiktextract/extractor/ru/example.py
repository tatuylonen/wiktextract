from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense

EXAMPLE_TEMPLATES = frozenset(["пример", "english surname example"])


def process_example_template(
    wxr: WiktextractContext,
    sense: Sense,
    template_node: TemplateNode,
):
    if template_node.template_name == "пример":
        process_пример_template(wxr, sense, template_node)
    elif template_node.template_name == "english surname example":
        process_en_surname_example_template(wxr, sense, template_node)


ПРИМЕР_TEMPLATE_ARG_MAPPING = {
    "автор": "author",
    "титул": "title",
    "дата": "date",
    "издание": "collection",
    "дата издания": "date_published",
    "ответственный": "editor",
    "перев": "translator",
    "источник": "source",
    2: "author",
    3: "title",
    4: "date",
    5: "collection",
    6: "date_published",
}


def process_пример_template(
    wxr: WiktextractContext,
    sense: Sense,
    template_node: TemplateNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:пример
    example = Example()
    for arg_name, arg_value in template_node.template_parameters.items():
        value = clean_node(wxr, None, arg_value)
        if len(value) == 0:
            continue
        if arg_name == 1:
            example.text = value
        elif arg_name == "текст":
            example.text = value
        elif arg_name == "перевод":
            example.translation = value
        elif arg_name in ПРИМЕР_TEMPLATE_ARG_MAPPING:
            field_name = ПРИМЕР_TEMPLATE_ARG_MAPPING[arg_name]
            if hasattr(example, field_name):
                setattr(example, field_name, value)
            else:
                wxr.wtp.debug(
                    f"Unknown {arg_name=} in example template {template_node}",
                    sortid="ru/example/process_example_template/54",
                )

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for span_node in expanded_node.find_html_recursively("span"):
        span_class = span_node.attrs.get("class", "")
        if "example-details" in span_class:
            example.ref = clean_node(wxr, None, span_node)
        elif "example-block" in span_class:
            calculate_bold_offsets(
                wxr, span_node, example.text, example, "bold_text_offsets"
            )
        elif "example-translate" in span_class:
            calculate_bold_offsets(
                wxr,
                span_node,
                example.translation,
                example,
                "bold_translation_offsets",
            )

    if len(example.text) > 0:
        sense.examples.append(example)


def process_en_surname_example_template(
    wxr: WiktextractContext,
    sense: Sense,
    template_node: TemplateNode,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:english_surname_example
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node),
        additional_expand={"english surname example"},
        pre_expand=True,
    )
    for node in expanded_node.find_child(NodeKind.TEMPLATE):
        if node.template_name == "пример":
            process_пример_template(wxr, sense, node)
