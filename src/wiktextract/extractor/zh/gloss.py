from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from .example import extract_examples
from .models import AltForm, Sense, WordEntry
from .tags import translate_raw_tags

# https://zh.wiktionary.org/wiki/Template:Label
LABEL_TEMPLATES = frozenset(["lb", "lbl", "label"])


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    gloss_data: Sense,
) -> None:
    lang_code = page_data[-1].lang_code
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = []
        raw_tags = []
        for node in list_item_node.children:
            if isinstance(node, TemplateNode):
                raw_tag = clean_node(wxr, None, node)
                if node.template_name in LABEL_TEMPLATES:
                    raw_tags.append(raw_tag.strip("()"))
                elif raw_tag.startswith("〈") and raw_tag.endswith("〉"):
                    raw_tags.append(raw_tag.strip("〈〉"))
                else:
                    gloss_nodes.append(node)
                if node.template_name in FORM_OF_TEMPLATES:
                    process_form_of_template(wxr, node, gloss_data)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                continue
            else:
                gloss_nodes.append(node)

        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            gloss_text = clean_node(wxr, gloss_data, nodes_without_ruby)
        else:
            ruby_data = []
            gloss_text = clean_node(wxr, gloss_data, gloss_nodes)
        new_gloss_data = gloss_data.model_copy(deep=True)
        new_gloss_data.raw_tags.extend(raw_tags)
        if len(gloss_text) > 0:
            new_gloss_data.glosses.append(gloss_text)
        if len(ruby_data) > 0:
            new_gloss_data.ruby = ruby_data

        has_nested_gloss = False
        if list_item_node.contain_node(NodeKind.LIST):
            for child_node in list_item_node.find_child(NodeKind.LIST):
                if child_node.sarg.endswith("#"):  # nested gloss
                    has_nested_gloss = True
                    extract_gloss(wxr, page_data, child_node, new_gloss_data)
                else:  # example list
                    extract_examples(wxr, new_gloss_data, child_node)

        if not has_nested_gloss and len(new_gloss_data.glosses) > 0:
            translate_raw_tags(new_gloss_data)
            page_data[-1].senses.append(new_gloss_data)


def process_form_of_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: Sense
) -> None:
    form_of_text = ""
    is_alt_of = template_node.template_name.startswith("alt")
    for param_key, param_value in template_node.template_parameters.items():
        if param_key in (2, 3, "alt"):
            param_value = clean_node(wxr, None, param_value)
            if len(param_value) > 0:
                form_of_text = param_value
    for form_of_word in form_of_text.split(","):
        form_of_word = form_of_word.strip()
        if len(form_of_word) > 0:
            form_of = AltForm(word=form_of_word)
            if is_alt_of:
                sense.alt_of.append(form_of)
            else:
                sense.form_of.append(form_of)

    sense.tags.append("alt-of" if is_alt_of else "form-of")


# https://zh.wiktionary.org/wiki/Category:/Category:之形式模板
FORM_OF_TEMPLATES = {
    "abbreviation of",
    "abbr of",
    "abstract noun of",
    "accusative of",
    "accusative plural of",
    "accusative singular of",
    "acronym of",
    "active participle of",
    "adj form of",
    "agent noun of",
    "alternative case form of",
    "alt case, altcaps",
    "alternative form of",
    "alt form, altform",
    "alternative plural of",
    "alternative reconstruction of",
    "alternative spelling of",
    "alt sp",
    "alternative typography of",
    "aphetic form of",
    "apocopic form of",
    "archaic form of",
    "archaic inflection of",
    "archaic spelling of",
    "aspirate mutation of",
    "attributive form of",
    "augmentative of",
    "broad form of",
    "causative of",
    "clipping of",
    "clip of",
    "combining form of",
    "comparative of",
    "construed with",
    "contraction of",
    "dated form of",
    "dated spelling of",
    "dative of",
    "dative plural of",
    "dative singular of",
    "definite singular of",
    "definite plural of",
    "deliberate misspelling of",
    "diminutive of",
    "dim of",
    "dual of",
    "eclipsis of",
    "eggcorn of",
    "elative of",
    "ellipsis of",
    "elongated form of",
    "endearing diminutive of",
    "endearing form of",
    "equative of",
    "euphemistic form of",
    "euphemistic spelling of",
    "eye dialect of",
    "female equivalent of",
    "feminine of",
    "feminine plural of",
    "feminine plural past participle of",
    "feminine singular of",
    "feminine singular past participle of",
    "form of",
    "former name of",
    "frequentative of",
    "future participle of",
    "genitive of",
    "genitive plural of",
    "genitive singular of",
    "gerund of",
    "h-prothesis of",
    "hard mutation of",
    "harmonic variant of",
    "honorific alternative case form of",
    "honor alt case",
    "imperative of",
    "imperfective form of",
    "indefinite plural of",
    "inflection of",
    "infl of",
    "informal form of",
    "informal spelling of",
    "initialism of",
    "init of",
    "iterative of",
    "lenition of",
    "masculine noun of",
    "masculine of",
    "masculine plural of",
    "masculine plural past participle of",
    "medieval spelling of",
    "men's speech form of",
    "misconstruction of",
    "misromanization of",
    "misspelling of",
    "missp",
    "mixed mutation of",
    "nasal mutation of",
    "negative of",
    "neuter plural of",
    "neuter singular of",
    "neuter singular past participle of",
    "nomen sacrum form of",
    "nominalization of",
    "nominative plural of",
    "nonstandard form of",
    "nonstandard spelling of",
    "noun form of",
    "nuqtaless form of",
    "obsolete form of",
    "obsolete spelling of",
    "obs sp",
    "obsolete typography of",
    "participle of",
    "passive of",
    "passive participle of",
    "passive past tense of",
    "past active participle of",
    "past participle form of",
    "past participle of",
    "past passive participle of",
    "past tense of",
    "pejorative of",
    "perfect participle of",
    "perfective form of",
    "plural of",
    "present active participle of",
    "present participle of",
    "present tense of",
    "pronunciation spelling of",
    "pronunciation variant of",
    "rare form of",
    "rare spelling of",
    "rare sp",
    "reflexive of",
    "rfform",
    "romanization of",
    "short for",
    "singular of",
    "singulative of",
    "slender form of",
    "soft mutation of",
    "spelling of",
    "standard form of",
    "standard spelling of",
    "stand sp",
    "superlative attributive of",
    "superlative of",
    "superlative predicative of",
    "superseded spelling of",
    "sup sp",
    "supine of",
    "syncopic form of",
    "synonym of",
    "syn of",
    "t-prothesis of",
    "uncommon form of",
    "uncommon spelling of",
    "verbal noun of",
    "verb form of",
    "vocative plural of",
    "vocative singular of",
}
