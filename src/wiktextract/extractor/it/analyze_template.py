from wikitextprocessor import Page, Wtp

SECTION_TITLE_TEMPLATES = {
    # POS titles
    # https://it.wiktionary.org/wiki/Categoria:Template_parti_del_discorso
    "Template:-acron-",
    "Template:-art-",
    "Template:-avv-",
    "Template:-class-",
    "Template:-cong-",
    "Template:-espr-",
    "Template:-hanzi-",
    "Template:-inter-",
    "Template:-kanpr-",
    "Template:-loc agg-",
    "Template:-loc avv-",
    "Template:-loc cong-",
    "Template:-loc inter-",
    "Template:-loc nom-",
    "Template:-loc nom form-",
    "Template:-loc prep-",
    "Template:-loc verb-",
    "Template:-nome form-",
    "Template:-nome-",
    "Template:-sost form-",
    "Template:-part-",
    "Template:-posp-",
    "Template:-prep-",
    "Template:-pron dim-",
    "Template:-pron indef-",
    "Template:-pron interrog-",
    "Template:-pron poss-",
    "Template:-pron rel-",
    "Template:-pron rifl-",
    "Template:-pronome-",
    "Template:-pron form-",
    "Template:-sost-",
    "Template:-voce verb-",
    # POS titles
    # https://it.wiktionary.org/wiki/Categoria:Template_aggiornati
    "Template:-agg-",
    "Template:-agg dim-",
    "Template:-agg nom-",
    "Template:-agg num-",
    "Template:-agg poss-",
    "Template:-cifr-",
    "Template:-lett-",
    "Template:-prefissoide-",
    "Template:-suffissoide-",
    "Template:-pref-",
    "Template:-interp-",
    "Template:-suff-",
    "Template:-verb-",
    # POS
    # https://it.wiktionary.org/wiki/Categoria:Template_per_gli_aggettivi
    "Template:-agg form-",
    "Template:-agg num form-",
    # other sections
    # https://it.wiktionary.org/wiki/Categoria:Template_sezione
    "Template:-esempio-",
    "Template:-iperon-",
    "Template:-ipon-",
    "Template:-noconf-",
    "Template:-rel-",
    "Template:-sill-",
    "Template:-sin-",
    "Template:-uso-",
    "Template:-var-",
    "Template:-alter-",
    "Template:-chat-",  # pos
    "Template:-coni-",
    "Template:-decl-",
    "Template:-der-",
    "Template:-fal-",  # pos
    "Template:-ref-",
    "Template:-pron-",
    "Template:-prov-",
    "Template:-trascrizione-",  # pos
    # https://it.wiktionary.org/wiki/Categoria:Template_vocabolo
    "Template:-etim-",
    "Template:-trad-",
    "Template:-ant-",
    "Template:-cod-",  # pos
    "Template:-carhi-",  # pos
    "Template:-quote-",
}


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    # don't pre-expand language title templates, like "-it-"
    return set(), page.title in SECTION_TITLE_TEMPLATES
