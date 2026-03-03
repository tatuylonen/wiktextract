import re

from wikitextprocessor import Page, Wtp

IGNORE_TEMAPLTES = frozenset(["--", "-rus-trans-", "-infocat-"])


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    title = page.title.removeprefix("Bản mẫu:")
    is_section = (
        title.startswith("-")
        and title.endswith("-")
        and title not in IGNORE_TEMAPLTES
    )
    if is_section and page.body is not None and len(page.body) > 0:
        # replace <h3> to ===
        new_body = re.sub(
            r"</?h(\d)>", lambda m: "=" * int(m.group(1)), page.body
        )
        if new_body != page.body:
            wtp.add_page(page.title, 10, body=new_body, need_pre_expand=True)

    return set(), is_section
