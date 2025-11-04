from typing import Union

from .models import WordEntry

# https://ru.wiktionary.org/wiki/Викисловарь:Условные_сокращения
# Стиль
STYLE_TAGS: dict[str, Union[str, list[str]]] = {
    "бран.": "offensive",
    "вульг.": "vulgar",
    "высок.": "honorific",
    "гипокор.": "familiar",
    "груб.": "vulgar",
    "детск.": "childish",
    "диал.": "dialectal",
    # "дисфм.": "дисфемизм",
    "жарг.": "slang",
    "ирон.": "ironic",
    "истор.": "historical",
    # "канц.": "канцелярское",
    "книжн.": "literary",
    "ласк.": "diminutive",
    # "мол.": "молодёжное",
    "нар.-поэт.": "poetic",
    "нар.-разг.": "colloquial",
    # "научн.": "научное",
    "неодобр.": "disapproving",
    "неол.": "neologism",
    "обсц.": "vulgar",
    "офиц.": "formal",
    # "патет.": "патетическое",
    "поэт.": "poetic",
    "презр.": "contemplative",
    "пренебр.": "derogatory",
    "прост.": "colloquial",
    # "проф.": "профессиональное",
    # "публиц.": "публицистическое",
    "разг.": "colloquial",
    "рег.": "regional",
    "ритор.": "rhetoric",
    "сленг.": "slang",
    "сниж.": "reduced",
    # "советск.": "советизм",
    "спец.": "special",
    "старин.": "archaic",
    "табу": "taboo",
    # "торж.": "торжественное",
    "трад.-нар.": "traditional",
    "трад.-поэт.": ["traditional", "poetic"],
    # "увелич.": "увеличительное",
    "уменьш.": "diminutive",
    "умласк.": ["diminutive", "endearing"],
    "унич.": "pejorative",
    "усилит.": "emphatic",
    "устар.": "obsolete",
    "фам.": "familiar",
    # "школьн.": "школьное",
    "шутл.": "humorous",
    "эвф.": "euphemistic",
    # "экзот.": "экзотизм",
    "экспр.": "expressively",
    # "эррат.": "эрративное",
    # Категория:Стилистические пометы
    "неофиц.": "informal",
    "одобр.": "approving",
    "сленг": "slang",
    "уважит.": "polite",
    "уничиж.": "derogatory",
}

# Предметные области
TOPICS = {
    "авиац.": "aeronautics",
    "автомоб.": "automotive",
    "агрон.": "agriculture",
    "алхим.": "pseudoscience",
    "альп.": "sports",
    "анат.": "medicine",
    "антроп.": "anthropology",
    "артилл.": "weaponry",
    "археол.": "history",
    "архит.": "architecture",
    "астрол.": "astrology",
    "астрон.": "astronomy",
    "библейск.": "religion",
    "биол.": "biology",
    "биохим.": "biochemistry",
    "ботан.": "botany",
    "бухг.": "finance",
    "вет.": "zoology pathology",
    "воен.": "military",
    "гастрон.": "medicine",
    "генет.": ["biology", "medicine"],
    "геогр.": "geography",
    "геод.": "geography",
    "геол.": "geology",
    "геометр.": "geometry",
    "геофиз.": "geology",
    "геральд.": "heraldry",
    "гидрол.": "geography",
    "гидротехн.": "engineering",
    "гляциол.": "geography",
    "горн.": "mining",
    "дипл.": "politics",
    "ж.-д.": "railways",
    "живоп.": "arts",
    # "животн.": "животноводство",
    "зоол.": "zoology",
    "игр.": "games",
    "информ.": "computing",
    "искусств.": "art-history",
    "ислам.": "Islam",
    "ихтиол.": "ichthyology",
    # "йогич.": "йогическое",
    "карт.": "card-games",
    "керам.": ["chemistry", "engineering"],
    "кино": "film",
    "кинол.": "dogs",
    "комп.": "computing",
    "косм.": "astronomy",
    "кулин.": "cuisine",
    # "культурол.": "культурологическое",
    "лес.": "business",
    "лингв.": "linguistics",
    "матем.": "mathematics",
    "машин.": "engineering",
    "мед.": "medicine",
    "металл.": "metallurgy",
    "метеорол.": "meteorology",
    "мех.": "mechanical-engineering",
    "микробиол.": "microbiology",
    "минер.": "mineralogy",
    "мифол,": "mythology",
    "морск.": "nautical",
    "муз.": "music",
    # "нефтегаз.": "нефтегазовая промышленность и нефтепереработка",
    "нумизм.": "numismatics",
    "океан.": "oceanography",
    "оккульт.": "mysticism",
    "опт.": ["physics", "engineering"],
    "орнитол.": "ornithology",
    "охотн.": "hunting",
    "палеонт.": "paleontology",
    "паразит.": "medicine",
    "парикмах.": "hairdressing",
    "плотн.": "carpentry",
    "полигр.": "printing",
    "полит.": "politics",
    "портн.": "textiles",
    "прогр.": "programming",
    "психиатр.": "psychiatry",
    "психол.": "psychology",
    "пчел.": "agriculture",
    "радио.": ["radio", "engineering"],
    "радиоэл.": ["radio", "electricity"],
    "рекл.": "marketing",
    "религ.": "religion",
    "рыбол.": "fishing",
    "с.-х.": "agriculture",
    "сексол.": "sexuality",
    # "скорн.": "скорняжное дело",
    "социол.": "sociology",
    # "спелеол.": "спелеологический",
    "спорт.": "sports",
    "стат.": "statistics",
    "столярн.": "carpentry",
    "строит.": "construction",
    "театр.": "theater",
    "текст.": "textiles",
    "телеком.": "telecommunications",
    "техн.": "engineering",
    "торг.": "commerce",
    "управл.": "management",
    "фант.": "fantasy",
    "фарм.": "pharmacology",
    "физ.": "physics",
    "физиол.": "physiology",
    "филат.": "philately",
    "филол.": "philology",
    "филос.": "philosophy",
    "фин.": "finance",
    "фолькл.": "folklore",
    "фотогр.": "photography",
    "хим.": "chemistry",
    "хоз.": "economics",
    # "хореогр.": "хореографическое",
    "церк.": "religion",
    "цирк.": "circus",
    "цитол.": "cytology",
    "шахм.": "chess",
    "швейн.": "sewing",
    "экол.": "ecology",
    "экон.": "economics",
    "эл.-техн.": "electrical-engineering",
    "эл.-энерг.": "electricity",
    "энтомол.": "entomology",
    "этногр": "ethnography",
    "этнолог.": "ethnology",
    "ювел.": "jewelry",
    "юр.": "legal",
    # Категория:Стилистические пометы
    "бизн.": "business",
}

# Жаргон
SLANG_TOPICS = {
    "автомоб. жарг.": "motorcycling",
    "арест.": "prison",
    "воен. жарг.": "military",
    "жарг. аним.": "anime",
    # "жарг. викип.": "жаргон википроектов"
    "интернет.": "Internet",
    "комп. жарг.": "computer",
    # "студ. жарг.": "студенческий жаргон",
    "техн. жарг.": "technical",
    "крим. и крим. жарг.": "criminology",
    "полит. жарг.": "politics",
    "жарг. нарк.": "drugs",
    "жарг. ЛГБТ": "LGBT",
    # "жарг. гом.": "жаргон гомосексуалов",
}

# Грамматические категории
GRAMMATICAL_TAGS = {
    "3л.": "impersonal",
    "адъектив.": "adjective",
    "безл.": "impersonal",
    "вводн. сл.": "parenthetic",
    "вин. п.": "accusative",
    "вопр.": "interrogative",
    # "восклиц.": "в восклицательных предложениях",
    "гл.": "verb",
    "дат. п.": "dative",
    "ед. ч.": "singular",  # Шаблон:ед
    "ж. р.": "feminine",
    "женск.": "feminine",
    "им. п.": "nominative",
    "исх. п.": "ablative",
    "исч.": "countable",
    "м. р.": "masculine",
    "местн. п.": "locative",
    "метоним.": "metonymically",
    "мн. ч.": "plural",  # Шаблон:мн, Шаблон:мн.
    "неисч.": "uncountable",
    "неодуш.": "inanimate",
    "неперех.": "intransitive",
    "нескл.": "indeclinable",
    # "обобщ": "",
    # "общ.": "",
    "одуш.": "animate",
    # "отриц.": "",
    "перех.": "transitive",
    # "повел.": "",
    "предик.": "predicative",
    # "предл. п.": "",
    "прил.": "adjective",
    # "прош.": "",
    # "разд. п.": "",
    "род. п.": "genitive",
    "собир.": "collective",
    "статив.": "stative",
    "субстантивир.": "substantive",
    "сущ.": "noun",
    "тв. п.": "instrumental",
    # https://ru.wiktionary.org/wiki/Категория:Шаблоны:Условные_сокращения
    "м.": "masculine",  # Шаблон:m
    "ср.": "neuter",  # Шаблон:n
    "ж.": "feminine",  # Шаблон:f
    "ж. мн.": ["feminine", "plural"],  # Шаблон:f.pl
    "несов.": "imperfective",  # Шаблон:impf
    "м./ж.": ["masculine", "feminine"],  # Шаблон:m/f
    "ср./м.": ["neuter", "masculine"],  # Шаблон:n/m
    "сов.": "perfective",  # Шаблон:pf
    # Шаблон:прил ru 1a^
    "муж. р.": "masculine",
    "ср. р.": "neuter",
    "жен. р.": "feminine",
    "неод.": "inanimate",
    "т.": "instrumental",
    "п.": "prepositional",
    "кратк. форма": "short-form",
    # Шаблон:мест ru п1*b
    "с.": "neuter",
    "в. (^(одуш.)/_(неодуш.))": ["accusative", "animate", "inanimate"],
    # Шаблон:словоформы tt
    "прит.": "possessive",
    "1-е": "first-person",
    "2-е": "second-person",
    "3-е": "third-person",
    # Template:гл ru ^bСВ
    "пр. действ. прош.": ["active", "participle", "past"],
    "деепр. прош.": ["adverbial", "participle", "past"],
    "пр. страд. прош.": ["passive", "participle", "past"],
    "прич. страд. прош.": ["passive", "participle", "past"],
    # Template:гл ru 2a
    "пр. действ. наст.": ["active", "participle", "present"],
    "деепр. наст.": ["adverbial", "participle", "present"],
    "пр. страд. наст.": ["passive", "participle", "present"],
}

# Прочие сокращения
OTHER_TAGS = {
    "букв.": "literary",
    # "искаж.": "искажённое",
    "неправ.": "irregular",
    "перен.": "figuratively",
    "редк.": "rare",
    # "тж.": "",  # Шаблон:тж.
    "общая": "indefinite",
    "опред.": "definite",
    "счётн.": "count-form",
    "наречия": "adverb",
    "имена собственные": "proper-noun",
    "причастия": "participle",
    "деепричастия": ["adverbial", "participle"],
    "топонимы": "toponymic",
    "неопр.": "indefinite",
    "опр.": "definite",
    "imperfectum": "imperfect",
    "perfectum": "perfect",
    "gerundium": "gerund",
    "gerundivum": "gerundive",
    "plusquamperfectum": "pluperfect",
    "инфинитив": "infinitive",
    "герундий": "gerund",
    "предикативы": "predicative",
    "сша": "USA",
    "превосх. формы": "superior",
    "местоимения": "pronoun",
    "ум.-ласк.": "diminutive",
    "междометия": "interjection",
    # Template:гл cu IV
    "аорист": "aorist",
    "нетемат.": "non-thematic",
    "темат.": "thematic",
    "предлоги": "prepositional",
    # Template:спряжение es short
    "modo indicativo": "indicative",
    "presente": "present",
    "futuro": "future",
    "pretérito indefinido": ["past", "indefinite"],
    "presente de subjuntivo": ["present", "subjunctive"],
    "yo": ["first-person", "singular"],
    "tú": ["second-person", "singular"],
    "él\nella\nusted": ["third-person", "singular"],
    "nosotros\nnosotras": ["first-person", "plural"],
    "vosotros\nvosotras": ["second-person", "plural"],
    "ellos\nellas\nustedes": ["third-person", "plural"],
    "participio": "participle",
    "gerundio": "gerund",
    # Template:спряжение pt short
    "indicativo": "indicative",
    "pretérito perfeito": ["past", "perfect"],
    "subjuntivo": "subjunctive",
    "imperativo": "imperative",
    "eu": ["first-person", "singular"],
    "tu": ["second-person", "singular"],
    "você\nele / ela": ["third-person", "singular"],
    "nós": ["first-person", "plural"],
    "vós": ["second-person", "plural"],
    "vocês\neles / elas": ["third-person", "plural"],
    # Template:спряжение fr short
    "indicatif": "indicative",
    "présent": "present",
    "futur simple": "future",
    "imparfait": ["past", "imperfect"],
    "conditionnel présent": ["present", "conditional"],
    "je": ["first-person", "singular"],
    "il\nelle": ["third-person", "singular"],
    "nous": ["first-person", "plural"],
    "vous": ["second-person", "plural"],
    "ils\nelles": ["third-person", "plural"],
    "participe passé": ["past", "participle"],
    "participe présent": ["present", "participle"],
    # Template:спряжение it short
    "passato remoto": "past-remote",
    "presente\ndi congiuntivo": ["present", "subjunctive"],
    "io": ["first-person", "singular"],
    "egli\nella\nlei": ["third-person", "singular"],
    "noi": ["first-person", "plural"],
    "voi": ["second-person", "plural"],
    "essi\nesse\nloro": ["third-person", "plural"],
    # Template:спряжение ro short
    "modul indicativ": "indicative",
    "prezent": "present",
    "imperfect": "imperfect",
    "perfectul compus": ["compound", "perfect"],
    "viitorul i": "future-i",
    "el\nea": ["third-person", "singular"],
    "voi\ndumneavoastră": ["second-person", "plural"],
    "ei\nele": ["third-person", "plural"],
    "conjunctiv, p. 3": ["conjunctive", "third-person"],
    "participiu": "participle",
    "gerunziu": "gerund",
    # Template:спряжение sw short
    "изъявительное наклонение": "indicative",
    "настоящее": "present",
    "имперфект": "imperfect",
    "перфект": "perfect",
    "mimi": ["first-person", "singular"],
    "wewe": ["second-person", "singular"],
    "yeye (люди)": ["third-person", "singular"],
    "yeye (вещи)": ["third-person", "singular", "non-human"],
    "sisi": ["first-person", "plural"],
    "nyinyi": ["second-person", "plural"],
    "wao (люди)": ["third-person", "plural"],
    "wao (вещи)": ["third-person", "plural", "non-human"],
    "хабитуалис": "habitual",
    # шаблона:спряжения
    "эта форма слова или ударение является нестандартной для данной схемы словоизменения": "nonstandard",
}

CASE_TAGS = {
    # Шаблон:сущ ru m a 1a
    "им.": "nominative",
    "р.": "genitive",
    "д.": "dative",
    "в.": "accusative",
    "тв.": "instrumental",
    "пр.": "prepositional",
    # Шаблон:сущ bg 7
    "зват.": "vocative",
    # Шаблон:сущ de (e)s er ern/n
    "ном.": "nominative",
    "ген.": "genitive",
    "дат.": "dative",
    "акк.": "accusative",
    # Шаблон:сущ cu (-а)
    # "м.": "locative",  # conflict with gender tag
    "местный": "locative",
    "зв.": "vocative",
    # Template:падежи la 3
    "абл.": "ablative",
    "вок.": "vocative",
    # Template:гл la 1
    "supinum i": "supine-i",
    "supinum ii": "supine-ii",
    # Template:падежи tr
    "вин.": "accusative",
    "мест.": "locative",
    "род.": "genitive",
    # Template:сущ ru m ina 1c
    "местный падеж": "locative",
    "разделительный падеж": "partitive",
}

TENSE_TAGS = {
    # Шаблон:Гл-блок
    "наст.": "present",
    "будущ.": "future",
    "прош.": "past",
    "будущее": "future",
    # Template:гл la 1
    "praesens": "present",
    "futūrum i": "future-i",
    "futūrum ii": "future-ii",
    "infīnitivus praesentis actīvi": ["infinitive", "present", "active"],
    "infīnitivus praesentis passīvi": ["infinitive", "present", "passive"],
    "participium praesentis actīvi": ["participle", "present", "active"],
    "infīnitivus perfecti actīvi": ["infinitive", "perfect", "active"],
    "participium perfecti passivi": ["participle", "perfect", "passive"],
    "participium futuri activi": ["participle", "future", "active"],
    # Template:гл en irreg
    "прош. вр.": "past",
    "прич. прош. вр.": ["past", "participle"],
    # Template:гл ru 2a-ся
    "наст./будущ.": ["present", "future"],
    # Template:гл ru 7b/b-дX
    "настоящее время": "present",
    "ед. число": "singular",
    "мн. число": "plural",
    "1-е лицо": "first-person",
    "2-е лицо": "second-person",
    "3-е лицо": "third-person",
    "прошедшее время": "past",
    "с. р.": "neuter",
    "повелительное наклонение": "imperative",
    "причастия": "participle",
    "действ. наст.": ["active", "present"],
    "действ. прош.": ["active", "past"],
    "страд. наст.": ["passive", "present"],
    "страд. прош.": ["passive", "past"],
    "деепричастия": ["adverbial", "participle"],
    "наст. вр.": "present",
    "будущее время": "future",
}

MOOD_TAGS = {
    # Шаблон:Гл-блок
    "повелит.": "imperative",
    # Template:гл la 1
    "indicatīvus": "indicative",
    "coniunctīvus": "conjunctive",
    "imperatīvus": "imperative",
}

PERSON_TAGS = {
    # Шаблон:Гл-блок
    "я": ["first-person", "singular"],
    "ты": ["second-person", "singular"],
    "он\nона\nоно": ["third-person", "singular"],
    "он\nона": ["third-person", "singular"],
    "мы": ["first-person", "plural"],
    "вы": ["second-person", "plural"],
    "они": ["third-person", "plural"],
    # Template:гл la 1
    "1 p.": "first-person",
    "2 p.": "second-person",
    "3 p.": "third-person",
    # Template:гл en irreg
    "3-е л. ед. ч.": ["third-person", "singular"],
}

VOICE_TAGS = {
    # Шаблон:Гл-блок
    "пр. действ.": "active",
    "деепр.": "adverbial",
    "пр. страд.": "passive",
    # Template:гл la 1
    "act.": "active",
    "pass.": "passive",
}

NUMBER_TAGS = {
    # Шаблон:сущ cu (-а)
    "дв. ч.": "dual",
    "часто мн. ч.": ["often", "plural"],
    # Template:гл la 1
    "sing.": "singular",
    "plur.": "plural",
    "sg.": "singular",
    "pl.": "plural",
}

TRANSLATION_TAGS = {
    # Шаблон:перев-блок
    # https://en.wikipedia.org/wiki/Azerbaijani_alphabet
    # https://ru.wiktionary.org/wiki/Модуль:languages/data
    "арабск.": "Arabic",
    "кир.": "Cyrillic",
    "лат.": "Latin",
    "лат": "Latin",
    "кана": "katakana",
    "сир.": "Syriac",
    "иуд.": "Jewish",
    "центральный": "Central",
    "демот.": "Demotic Greek",
    "кафар.": "Katharevousa",
    "мальдивский": "Maldivian",
    "традиц.": "traditional",
    "у": "Wu",
    "упрощ.": "simplified",
    "южноминьский": "Min",
    "курманджи": "Kurmanji",
    "сорани": "Sorani",
    "севернокурдский": "Kurmanji",
    "южнокурдский": "Southern Kurdish",
    "кириллица": "Cyrillic",
    "глаголица": "Glagolitic",
    "араб.": "Arabic",
    "письменный": "Written-Form",  # italic tag
    "устный": "colloquial",
}

MORPHOLOGICAL_TEMPLATE_TAGS = {
    # "Шаблон:inflection/ru/noun/text" used in "сущ-ru"
    "одушевлённое": "animate",
    "неодушевлённое": "inanimate",
    "одушевлённое или неодушевлённое": ["animate", "inanimate"],
    "неодушевлённое или одушевлённое": ["animate", "inanimate"],
    "мужской род": "masculine",
    "женский род": "feminine",
    "средний род": "neuter",
    "общий род (может согласовываться с другими частями речи как мужского": "common",  # noqa: E501
    "мужской или женский род": ["masculine", "feminine"],
    "мужской или средний род": ["masculine", "neuter"],
    "женский или мужской род": ["masculine", "feminine"],
    "женский или средний род": ["feminine", "neuter"],
    "средний или мужской род": ["masculine", "neuter"],
    "средний или женский род": ["feminine", "neuter"],
    "несклоняемое": "indeclinable",
    "адъективное": "adjective",
    "местоименное": "pronominal",
    # https://en.wikipedia.org/wiki/Russian_declension
    "1-е": "declension-1",
    "2-е": "declension-2",
    "3-е": "declension-3",
    "2-е (5-e)": ["declension-1", "declension-5"],
    # Шаблон:inflection/ru/adj
    "качественное": "qualitative",
    "относительное": "relative",
    "притяжательное": "possessive",
    # verb tags from "Шаблон:Гл-блок"
    "совершенный вид": "perfect",
    "несовершенный вид": "imperfective",
    "двувидовой": "biaspectual",
    "непереходный": "intransitive",
    "переходный": "transitive",
    "безличный": "impersonal",
    "возвратный": "reflexive",
}

ALL_TAGS = {
    **STYLE_TAGS,
    **GRAMMATICAL_TAGS,
    **OTHER_TAGS,
    **CASE_TAGS,
    **TENSE_TAGS,
    **MOOD_TAGS,
    **PERSON_TAGS,
    **VOICE_TAGS,
    **NUMBER_TAGS,
    **TRANSLATION_TAGS,
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        raw_tag_lower = raw_tag.lower()
        if raw_tag_lower in ALL_TAGS:
            tr_data = ALL_TAGS[raw_tag_lower]
            if isinstance(tr_data, str):
                data.tags.append(tr_data)
            elif isinstance(tr_data, list):
                data.tags.extend(tr_data)
        elif hasattr(data, "topics"):
            tr_data = ""
            if raw_tag_lower in TOPICS:
                tr_data = TOPICS[raw_tag_lower]
            elif raw_tag_lower in SLANG_TOPICS:
                tr_data = SLANG_TOPICS[raw_tag_lower]
                if "slang" not in data.tags:
                    data.tags.append("slang")
            if isinstance(tr_data, str) and len(tr_data) > 0:
                data.topics.append(tr_data)
            elif isinstance(tr_data, list):
                data.topics.extend(tr_data)
            else:
                raw_tags.append(raw_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
