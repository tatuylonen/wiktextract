from wikitextprocessor import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_tabs_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:Tabs
    tags = [
        ["masculine", "singular"],
        ["masculine", "plural"],
        ["feminine", "singular"],
        ["feminine", "plural"],
    ]
    for arg_name in range(1, 5):
        arg_value = clean_node(
            wxr, None, node.template_parameters.get(arg_name, "")
        )
        if arg_value not in ["", wxr.wtp.title]:
            form = Form(form=arg_value, tags=tags[arg_name - 1])
            word_entry.forms.append(form)
