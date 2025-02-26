from wikitextprocessor import Page, Wtp

SECTION_TITLE_TEMPLATES = {
    "Templat:ulang",
    "Templat:zh-num",
    "Templat:zh-inter",
}


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    # https://id.wiktionary.org/wiki/Wikikamus:Penjelasan_tataletak_entri
    # https://id.wiktionary.org/wiki/Kategori:Templat_kelas_kata
    # https://id.wiktionary.org/wiki/Kategori:Templat_umum
    # https://id.wiktionary.org/wiki/Kategori:Templat_bahasa
    return (
        set(),
        page.title in SECTION_TITLE_TEMPLATES
        or (page.title.startswith("Templat:-") and page.title.endswith("-"))
        or (page.title.startswith("Templat:=") and page.title.endswith("="))
        or page.title.startswith(
            (
                "Templat:imbuhan ",
                "Templat:sisipan ",
                "Templat:ulang ",
                "Templat:verba ",
                "Templat:nomina ",
            )
        )
        or page.title.endswith(
            ("proper noun", "-aj", "-av", "-nm", "-vb", "-prnc")
        ),
    )
