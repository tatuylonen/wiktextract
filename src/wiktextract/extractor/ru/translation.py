from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, WikiNode

from wiktextract.extractor.ru.models import Translation, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_translations(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level3_node: WikiNode,
):
    sense = None
    for template_node in level3_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "перев-блок":
            gloss_nodes = template_node.template_parameters.get(1, [])
            if gloss_nodes:
                sense = clean_node(wxr, {}, gloss_nodes).strip()
            for key, raw_value in template_node.template_parameters.items():
                if isinstance(key, str):
                    lang_code = key
                    lang = code_to_name(lang_code, "ru")

                    for value_node in (
                        raw_value
                        if isinstance(raw_value, list)
                        else [raw_value]
                    ):
                        if (
                            isinstance(value_node, WikiNode)
                            and value_node.kind == NodeKind.LINK
                        ):
                            word = clean_node(wxr, {}, value_node).strip()
                            if word:
                                word_entry.translations.append(
                                    Translation(
                                        lang_code=lang_code,
                                        lang=lang,
                                        word=word,
                                        sense=sense if sense else None,
                                    )
                                )
                        # XXX: Extract non link content such as tags

        else:
            wxr.wtp.debug(
                f"Found unexpected template {template_node.template_name} in translation section",
                sortid="extractor/ru/translation/extract_translations/100",
            )
            pass
