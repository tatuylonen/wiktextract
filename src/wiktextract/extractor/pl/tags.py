from .models import WordEntry

# Help:Abbreviations used in Wiktionary
# https://pl.wiktionary.org/wiki/Pomoc:Skróty_używane_w_Wikisłowniku
# Category:Shortcut templates
# https://pl.wiktionary.org/wiki/Kategoria:Szablony_skrótów
TAGS = {
    "abl.": "ablative",
    # "akust.": "",
    "aor.": "aorist",
    "bezok.": "infinitive",
    "bezosob.": "impersonal",
    "bibl.": "Biblical",
    "blm": "no-plural",
    "blp": "no-singulative",
    "Bm": "Bokmål",
    "bośn.": "Bosnian",
    "brytań.": "British",
    "bułg.": "Bulgarian",
    "bwr.": "Bavarian",
    # Category:Acronym templates - grammar
    # https://pl.wiktionary.org/wiki/Kategoria:Szablony_skrótów_-_gramatyka
    "m": "masculine",
    # gender types in POS line
    "męski": "masculine",
    "męskozwierzęcy": ["masculine", "animate"],
    "męskorzeczowy": ["masculine", "inanimate"],
    "niepoliczalny": "uncountable",
    "nieżywotny": "inanimate",
    "nijaki": "neuter",
    "policzalny": "countable",
    "przechodni": "transitive",
    "żeński": "feminine",
    "żywotny": "animate",
    # sound tags
    "bryt. (RP)": ["British", "Received-Pronunciation"],
    "amer.": "US",
    "lm": "plural",
    "lp": "singular",
}

TOPICS = {
    "adm.": "administration",
    "agrot.": "agrotechnology",
    "alch.": "alchemy",
    "anat.": "anatomy",
    "antrop.": "anthropology",
    "arachn.": "arachnology",
    "archit.": "architecture",
    "archeol.": "archeology",
    "astr.": "astronomy",
    "astrol.": "astrology",
    "astronaut.": "astronautics",
    "bank.": "banking",
    # "bibliot.": "",
    "biochem.": "biochemistry",
    "biol.": "biology",
    # "biur.": "",
    "bot.": "botany",
    "bud.": "construction",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tag = TAGS[raw_tag]
            if isinstance(tag, str):
                data.tags.append(tag)
            elif isinstance(tag, list):
                data.tags.extend(tag)
        elif raw_tag in TOPICS and hasattr(data, "topics"):
            topic = TOPICS[raw_tag]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, list):
                data.topics.extend(topic)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
