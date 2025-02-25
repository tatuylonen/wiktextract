from wikitextprocessor import Page, Wtp

# https://id.wiktionary.org/wiki/Wikikamus:Penjelasan_tataletak_entri
# https://id.wiktionary.org/wiki/Kategori:Templat_kelas_kata
# https://id.wiktionary.org/wiki/Kategori:Templat_umum
SECTION_TITLE_TEMPLATES = {
    "Templat:-adj-",
    "Templat:-adv-",
    "Templat:-akronim-",
    "Templat:-art-",
    "Templat:-GantiDenganKelasKata-",
    "Templat:-gol-",
    "Templat:-inter-",
    "Templat:-intero-",
    "Templat:-kon-",
    "Templat:-nom-",
    "Templat:-nom-ulang-",
    "Templat:-num-",
    "Templat:-part-",
    "Templat:-prep-",
    "Templat:-pronom-",
    "Templat:-sub-",
    "Templat:-verb-",
    "Templat:=adj=",
    "Templat:=adv=",
    "Templat:=inter=",
    "Templat:=intero=",
    "Templat:=kon=",
    "Templat:=nom=",
    "Templat:=num=",
    "Templat:=p=",
    "Templat:=part=",
    "Templat:=prep=",
    "Templat:=pron=",
    "Templat:=pronom=",
    "Templat:=verb=",
    "Templat:ulang",
    "Templat:-sdd-",
}


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    return (
        set(),
        page.title in SECTION_TITLE_TEMPLATES
        or page.title.startswith(
            (
                "Templat:imbuhan ",
                "Templat:sisipan ",
                "Templat:ulang ",
                "Templat:verba ",
                "Templat:nomina ",
            )
        )
        or page.title.endswith(("proper noun", "-nm")),
    )
