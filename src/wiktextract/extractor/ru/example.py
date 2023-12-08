from wikitextprocessor import WikiNode

from wiktextract.extractor.ru.models import Example, Reference, Sense
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
    example = Example()
    reference = Reference()
    for key, value_raw in template_node.template_parameters.items():
        value = clean_node(wxr, {}, value_raw).strip()
        if not value:
            continue
        if isinstance(key, int) and key == 1:
            example.text = value

        else:
            key = clean_node(wxr, {}, key) if not isinstance(key, int) else key
            if key == "текст":
                example.text = value
            elif key == "перевод":
                example.translation = value
            elif key in EXAMPLE_TEMPLATE_KEY_MAPPING:
                field_name = EXAMPLE_TEMPLATE_KEY_MAPPING.get(key, key)
                if field_name in reference.model_fields:
                    setattr(reference, field_name, value)
                else:
                    wxr.wtp.debug(
                        f"Unknown key {key} in example template {template_node}",
                        sortid="wiktextract/extractor/ru/example/process_example_template/54",
                    )

    if example.model_dump(exclude_defaults=True) != {}:
        if reference.model_dump(exclude_defaults=True) != {}:
            example.ref = reference

        sense.examples.append(example)
