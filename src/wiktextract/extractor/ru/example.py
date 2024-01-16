from wikitextprocessor import WikiNode

from wiktextract.extractor.ru.models import Example, Sense
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

EXAMPLE_TEMPLATE_KEY_MAPPING = {
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


def process_example_template(
    wxr: WiktextractContext,
    sense: Sense,
    template_node: WikiNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:пример
    example = Example()
    for key, value_raw in template_node.template_parameters.items():
        value = clean_node(wxr, None, value_raw)
        if len(value) == 0:
            continue
        if isinstance(key, int) and key == 1:
            example.text = value
        else:
            if key == "текст":
                example.text = value
            elif key == "перевод":
                example.translation = value
            elif key in EXAMPLE_TEMPLATE_KEY_MAPPING:
                field_name = EXAMPLE_TEMPLATE_KEY_MAPPING.get(key, key)
                if field_name in example.model_fields:
                    setattr(example, field_name, value)
                else:
                    wxr.wtp.debug(
                        f"Unknown {key=} in example template {template_node}",
                        sortid="ru/example/process_example_template/54",
                    )

    if len(example.model_dump(exclude_defaults=True)) > 0:
        sense.examples.append(example)
