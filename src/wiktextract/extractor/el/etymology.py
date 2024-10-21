from wikitextprocessor import WikiNode
from wikitextprocessor.core import TemplateArgs
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.clean import clean_value
from wiktextract.page import clean_node

from .models import TemplateData, WordEntry
from .parse_utils import ETYMOLOGY_TEMPLATES, PANEL_TEMPLATES
from .pos import process_pos
from .section_titles import POS_HEADINGS
from .text_utils import ENDING_NUMBER_RE


def process_etym(
    wxr: WiktextractContext,
    base_data: WordEntry,
    node: WikiNode,
    title: str,
    title_num: int,
) -> list[WordEntry]:
    """Extract etymological data from section and process POS children."""
    # Get everything except subsections, which we assume are POS nodes.
    etym_contents = list(node.invert_find_child(LEVEL_KIND_FLAGS))
    etym_templates = []

    # A post-template_fn already has the expanded string from the template.
    # If we'd want to suppress something without bothering to expand it,
    # we can use a normal template_fn and return an empty string there.
    # But returning an empty string here will also do the same thing.
    # Returning None means "use whatever we expanded", default behavior.
    def post_etym_template_fn(
        name: str, ht: TemplateArgs, expanded: str
    ) -> str | None:
        """Collect parameters of templates in etymology section into
        `etymology_templates` field."""
        lname = name.lower().strip()
        if lname in PANEL_TEMPLATES:
            return ""
        if lname in ETYMOLOGY_TEMPLATES:
            # there are a bunch of clean_ functions: clean_value is to remove
            # italics and html tags and stuff like that from strings.
            expanded = clean_value(wxr, expanded)
            new_args = {}
            for k, v in ht.items():
                new_args[str(k)] = str(v)
            tdata = TemplateData(name=name, args=new_args, expansion=expanded)
            etym_templates.append(tdata)
        return None

    etym_text = clean_node(
        wxr, base_data, etym_contents, post_template_fn=post_etym_template_fn
    )

    if etym_text:
        base_data.etymology_text = etym_text
        if etym_templates:
            base_data.etymology_templates = etym_templates

        # logprint = []
        # for t in etym_templates:
        #     logprint.append(f"=== {t.name}")
        # lp = '\n'.join(logprint)
        # logger.info(f"{wxr.wtp.title}\n{lp}")

    ret: list[WordEntry] = []
    # Let's try to get some Part of Speech sections.
    for subheading in node.find_child(LEVEL_KIND_FLAGS):
        heading_title = (
            clean_node(wxr, None, subheading.largs[0]).lower().strip()
        )

        if m := ENDING_NUMBER_RE.search(heading_title):
            heading_num = int(m.group(0).strip())
            heading_title = heading_title[: m.start()]
        else:
            heading_num = -1  # default: see models.py/Sense

        new_data: list[WordEntry] = []
        if heading_title in POS_HEADINGS:
            pos_data = base_data.model_copy(deep=True)
            # Assume we'll get only one WordEntry or nothing.
            if (
                nd := process_pos(
                    wxr, subheading, pos_data, heading_title, heading_num
                )
            ) is not None:
                new_data.append(nd)
        else:
            ...

        if new_data is not None:
            # new_data would be one WordEntry object, for one Part of
            # Speech section ("Noun", "Verb"); this is generally how we
            # want it.
            ret.extend(new_data)

    return ret
