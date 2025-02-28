import re

from wikitextprocessor import Page, Wtp

# https://nl.wiktionary.org/wiki/Categorie:Woordsoortsjablonen
# some template in this category are not section titles, like "-liart-" and
# "-liart2-"
POS_TEMPLATES = frozenset(
    {
        "Sjabloon:-abbr-",
        "Sjabloon:-adjc-",
        "Sjabloon:-adverb-",
        "Sjabloon:-adverb-num-",
        "Sjabloon:-art-",
        "Sjabloon:-cijfer-",
        "Sjabloon:-circumf-",
        "Sjabloon:-conj-",
        "Sjabloon:-cont-",
        "Sjabloon:-ideo-",
        "Sjabloon:-interf-",
        "Sjabloon:-interj-",
        "Sjabloon:-leesteken-",
        "Sjabloon:-letter-",
        "Sjabloon:-name-",
        "Sjabloon:-noun-",
        "Sjabloon:-num-",
        "Sjabloon:-num-distr-",
        "Sjabloon:-num-indef-",
        "Sjabloon:-num-int-",
        "Sjabloon:-num-srt-",
        "Sjabloon:-ordn-",
        "Sjabloon:-ordn-indef-",
        "Sjabloon:-prcp-",
        "Sjabloon:-phrase-",
        "Sjabloon:-post-",
        "Sjabloon:-pref-",
        "Sjabloon:-prep-",
        "Sjabloon:-prep-form-",
        "Sjabloon:-pron-adv-",
        "Sjabloon:-pronom-dem-",
        "Sjabloon:-pronom-excl-",
        "Sjabloon:-pronom-indef-",
        "Sjabloon:-pronom-int-",
        "Sjabloon:-pronom-int2-",
        "Sjabloon:-pronom-pers-",
        "Sjabloon:-pronom-pos-",
        "Sjabloon:-pronom-rec-",
        "Sjabloon:-pronom-refl-",
        "Sjabloon:-pronom-rel-",
        "Sjabloon:-pronom-temp-",
        "Sjabloon:-pronoun-",
        "Sjabloon:-prtc-",
        "Sjabloon:-suff-",
        "Sjabloon:-symbool-",
        "Sjabloon:-verb-",
    }
)

# https://nl.wiktionary.org/wiki/Categorie:Lemmasjablonen
# some templates in this category are not section: "-demo-", "-telw-"
SECTION_TEMPLATES = frozenset(
    {
        "Sjabloon:-note-belg-nld-niet-standaard-",
        "Sjabloon:-relcat-",
        "Sjabloon:-writ-koppelteken-",
        "Sjabloon:-ana-",
        "Sjabloon:-ant-",
        "Sjabloon:-car-",
        "Sjabloon:-conjug-",
        "Sjabloon:-decl-",
        "Sjabloon:-desc-",
        "Sjabloon:-drv-",
        "Sjabloon:-etym-",
        "Sjabloon:-expr-",
        "Sjabloon:-fixedprep-",
        "Sjabloon:-hiero-",  # language
        "Sjabloon:-holo-",
        "Sjabloon:-homo-",
        "Sjabloon:-hyper-",
        "Sjabloon:-hypo-",
        "Sjabloon:-hypo-tax",
        "Sjabloon:-info dp-",
        "Sjabloon:-info-",
        "Sjabloon:-mero-",
        "Sjabloon:-note-",
        "Sjabloon:-par-",
        "Sjabloon:-preval-",
        "Sjabloon:-pron-",
        "Sjabloon:-prov-",
        "Sjabloon:-quot-",
        "Sjabloon:-ref-",
        "Sjabloon:-rel-",
        "Sjabloon:-rijm-",
        "Sjabloon:-syll-",
        "Sjabloon:-syn-",
        "Sjabloon:-trans-",
        "Sjabloon:-typ-",
        "Sjabloon:-writ-",
    }
)


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    # pre-expand section templates, like "=nld=", "-pron-"
    # don't expand "=="
    # don't expand inflection table templates like "-nlnoun-"
    need_pre_expand = (
        re.fullmatch(r"Sjabloon:=.+=", page.title) is not None
        or page.title in POS_TEMPLATES
        or page.title in SECTION_TEMPLATES
    )

    # magic word breaks level2 node in "=qtu=" template
    if (
        need_pre_expand
        and page.body is not None
        and page.body.startswith("__NOEDITSECTION__")
    ):
        wtp.add_page(
            page.title, 10, page.body.removeprefix("__NOEDITSECTION__").strip()
        )

    return set(), need_pre_expand
