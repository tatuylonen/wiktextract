from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import HTMLNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Form, WordEntry


def extract_conjugation(wxr: WiktextractContext, entry: WordEntry) -> None:
    """
    Find and extract conjugation page.

    https://fr.wiktionary.org/wiki/Conjugaison:français
    https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles/Français/Conjugaison
    https://fr.wiktionary.org/wiki/Aide:Conjugaisons
    """
    conj_ns = wxr.wtp.NAMESPACE_DATA["Conjugaison"]
    conj_page_title = (
        f"{conj_ns['name']}:{entry.lang.lower()}/{entry.word}"
    )
    conj_page = wxr.wtp.get_page_body(conj_page_title, conj_ns["id"])
    if conj_page is None:
        return
    conj_root = wxr.wtp.parse(conj_page)
    for conj_template in conj_root.find_child(NodeKind.TEMPLATE):
        if conj_template.template_name.startswith("fr-conj-"):
            process_fr_conj_template(wxr, entry, conj_template)


def process_fr_conj_template(
    wxr: WiktextractContext, entry: WordEntry, template_node: TemplateNode
) -> None:
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_conjugaison_en_français
    # https://fr.wiktionary.org/wiki/Modèle:fr-conj-1-ger
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    h3_text = ""
    for node in expanded_template.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.HTML:
            if node.tag == "h3":
                h3_text = clean_node(wxr, None, node)
            elif node.tag == "div":
                if h3_text == "Modes impersonnels":
                    process_fr_conj_modes_table(wxr, entry, node)
                else:
                    process_fr_conj_table(wxr, entry, node, h3_text)


def process_fr_conj_modes_table(
    wxr: WiktextractContext, entry: WordEntry, div_node: HTMLNode
) -> None:
    # the first "Modes impersonnels" table
    for table_node in div_node.find_child(NodeKind.TABLE):
        for row_index, row in enumerate(
            table_node.find_child(NodeKind.TABLE_ROW)
        ):
            if row_index == 0:
                continue  # skip header
            form_text = ""
            tags = ["Modes impersonnels"]
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                if cell_index == 0:
                    tags.append(clean_node(wxr, None, cell))
                elif cell_index % 3 == 0:
                    form = Form(
                        form=form_text,
                        tags=tags.copy(),
                        ipas=[clean_node(wxr, None, cell)],
                        source="Conjugaison page",
                    )
                    form.tags.append("Présent" if cell_index == 3 else "Passé")
                    entry.forms.append(form)
                    form_text = ""
                else:
                    if len(form_text) > 0:
                        form_text += " "
                    form_text += clean_node(wxr, None, cell)


def process_fr_conj_table(
    wxr: WiktextractContext, entry: WordEntry, div_node: HTMLNode, h3_text: str
) -> None:
    for table_node in div_node.find_child(NodeKind.TABLE):
        for row_index, row in enumerate(
            table_node.find_child(NodeKind.TABLE_ROW)
        ):
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                for cell_child in cell.children:
                    if isinstance(cell_child, WikiNode):
                        if (
                            cell_child.kind == NodeKind.HTML
                            and cell_child.tag == "table"
                        ):
                            process_fr_conj_html_table(
                                wxr, entry, cell_child, h3_text
                            )
                        elif cell_child.kind == NodeKind.TABLE:
                            process_fr_conj_wiki_table(
                                wxr, entry, cell_child, h3_text
                            )


def process_fr_conj_html_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    table_node: HTMLNode,
    h3_text: str,
):
    tags = [h3_text]
    for tr_index, tr_node in enumerate(table_node.find_html_recursively("tr")):
        if tr_index == 0:
            tags.append(clean_node(wxr, None, tr_node.children))
        else:
            form = Form(tags=tags, source="Conjugaison page")
            for td_index, td_node in enumerate(
                tr_node.find_html_recursively("td")
            ):
                if td_index < 2:
                    if len(form.form) > 0:
                        form.form += " "
                    form.form += clean_node(wxr, None, td_node)
                else:
                    if len(form.ipas) > 0:
                        form.ipas[0] += " "
                        form.ipas[0] += clean_node(wxr, None, td_node)
                    else:
                        form.ipas.append(clean_node(wxr, None, td_node))
            entry.forms.append(form)


def process_fr_conj_wiki_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    table_node: WikiNode,
    h3_text: str,
):
    tags = [h3_text]
    for row_index, row in enumerate(table_node.find_child(NodeKind.TABLE_ROW)):
        if row_index == 0:
            tags.append(clean_node(wxr, None, row.children))
        else:
            form = Form(tags=tags, source="Conjugaison page")
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                if cell_index < 2:
                    if len(form.form) > 0:
                        form.form += " "
                    form.form += clean_node(wxr, None, cell.children)
                else:
                    form.ipas.append(clean_node(wxr, None, cell.children))
            entry.forms.append(form)
