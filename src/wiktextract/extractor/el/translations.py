from typing import TypeAlias

from mediawiki_langcodes import code_to_name
from wikitextprocessor import (
    WikiNode,
)
from wikitextprocessor.core import TemplateArgs

from wiktextract import WiktextractContext
from wiktextract.page import clean_node

from .models import Translation, WordEntry

# Greek Wiktionary translation sections seem to be a hidden div, inside
# which is a table with one row and one cell with a list of translations.
# I don't know why there's a table, the div is what creates the columns.
# Each entry seems to generally use a {{τ|lang_code|translation|...}} template
# with perfect information.

LangCode: TypeAlias = str


def process_translations(
    wxr: WiktextractContext, data: WordEntry, translation_node: WikiNode
) -> None:
    """Takes a translation section node and extract template data."""

    current_sense: str = ""
    translations: list[Translation] = []

    def translation_template_fn(name: str, ht: TemplateArgs) -> str | None:
        nonlocal current_sense
        nonlocal translations

        if name == "μτφ-αρχή":
            current_sense = clean_node(wxr, None, ht.get(1, ""))
            # print(f"{current_sense=}")
        if name in ("τ", "t"):
            lang_code = ht.get(1, "")
            lang_name = code_to_name(lang_code)
            if not lang_code:
                wxr.wtp.warning(
                    f"Language-code '{lang_code}' in "
                    "translation does not parse.",
                    sortid="translations/57",
                )
                lang_name = "LANG_NAME_ERROR"
            text = ht.get(2, "")
            if not text:
                wxr.wtp.wiki_notice(
                    f"Translation template has no translation," f"{ht=}",
                    sortid="translations/64",
                )
                return None
            latin_translitteration = ht.get("tr", "")

            translations.append(
                Translation(
                    sense=current_sense,
                    lang_code=lang_code,
                    lang=lang_name,
                    word=text,
                    roman=latin_translitteration
                )
            )

        # print(f"{name=} -> {ht=}")
        return None

    # _ for discarding the return value; we're only using node_to_html
    # with the template_fn to capture template data.
    _ = wxr.wtp.node_to_html(
        translation_node,
        template_fn=translation_template_fn,
    )
    data.translations = translations
    # print(f"{translations=}")
