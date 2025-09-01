from wikitextprocessor import Page, Wtp

IGNORE_TEMAPLTES = frozenset(["--", "-rus-trans-", "-infocat-"])


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    title = page.title.removeprefix("Bản mẫu:")
    return set(), title.startswith("-") and title.endswith(
        "-"
    ) and title not in IGNORE_TEMAPLTES
