from typing import Optional, Union

from wikitextprocessor import WikiNode
from wikitextprocessor.core import TemplateArgs
from wiktextract import WiktextractContext
from wiktextract.clean import clean_value
from wiktextract.page import clean_node
from wiktextract.wxr_logging import logger

from .models import TemplateData, WordEntry
from .parse_utils import ETYMOLOGY_TEMPLATES, PANEL_TEMPLATES


def process_etym(
    wxr: WiktextractContext,
    etym_nodes: list[Union[str, WikiNode]],
    target_data: WordEntry,
) -> None:
    etym_templates = []

    def post_etym_template_fn(
        name: str, ht: TemplateArgs, expanded: str
    ) -> Optional[str]:
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
