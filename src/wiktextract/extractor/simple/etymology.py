from wikitextprocessor import WikiNode
from wikitextprocessor.core import TemplateArgs
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.clean import clean_value
from wiktextract.page import clean_node

from .models import TemplateData, WordEntry
from .parse_utils import ETYMOLOGY_TEMPLATES, PANEL_TEMPLATES


def process_etym(
    wxr: WiktextractContext,
    node: WikiNode,
    target_data: WordEntry,
) -> None:
    """Extract etymological data from section."""
    # Get everything except subsections.
    etym_nodes = list(node.invert_find_child(LEVEL_KIND_FLAGS))
    etym_templates = []

    def post_etym_template_fn(
        name: str, ht: TemplateArgs, expanded: str
    ) -> str | None:
        lname = name.lower().strip()
        if lname in PANEL_TEMPLATES:
            return ""
        if lname in ETYMOLOGY_TEMPLATES:
            expanded = clean_value(wxr, expanded)
            new_args = {}
            for k, v in ht.items():
                new_args[str(k)] = str(v)
            tdata = TemplateData(name=name, args=new_args, expansion=expanded)
            etym_templates.append(tdata)
        return None

    etym_text = clean_node(
        wxr, target_data, etym_nodes, post_template_fn=post_etym_template_fn
    )

    if etym_text:
        target_data.etymology_text = etym_text
        if etym_templates:
            target_data.etymology_templates = etym_templates

        # logprint = []
        # for t in etym_templates:
        #     logprint.append(f"=== {t.name}")
        # lp = '\n'.join(logprint)
        # logger.info(f"{wxr.wtp.title}\n{lp}")
