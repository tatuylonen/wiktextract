import contextlib
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from wiktextract.page import parse_page
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import keep_only_requested_language_sections
from wikitextprocessor import Wtp
from wikitextprocessor.interwiki import init_interwiki_map
from cache import PostgresCache, build_cache

import lupa
import lupa.lua52
from wiktextract.wxr_context import WiktextractContext
lupa._newest_lib = lupa.lua52


USER_AGENT = "live-lookup/0.1"
ERROR_MARKER_RE = re.compile(
    r'<strong class="error">Template:([^<]+)</strong>')
REDIRECT_RE = re.compile(
    r"^\s*#REDIRECT\s*:?\s*\[\[\s*([^\]|]+?)\s*(?:\|[^\]]*)?\]\]", re.IGNORECASE)
TEMPLATE_CALL_RE = re.compile(r"\{\{\s*([^{}|]+?)\s*(?:\||\}\})")


def open_with_retry(req: urllib.request.Request, max_retries: int = 5) -> bytes:
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == max_retries:
                raise
            wait = int(e.headers.get("Retry-After", 5))
            time.sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


def fetch_raw_wikitext(edition: str, title: str) -> str | None:
    url = f"https://{edition}.wiktionary.org/w/index.php?{urllib.parse.urlencode({'title': title, 'action': 'raw'})}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        return open_with_retry(req).decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def mediawiki_opensearch(edition: str, query: str, limit: int = 10) -> list[str]:
    """ used to suggest spellings when a direct page lookup finds nothing, 
    since live-lookup has no corpus of its own to search across"""
    params = {
        "action": "opensearch",
        "search": query,
        "namespace": "0",
        "limit": str(limit),
        "format": "json",
    }
    url = f"https://{edition}.wiktionary.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    data = json.loads(open_with_retry(req).decode("utf-8"))
    return data[1] if len(data) > 1 else []


def find_template_call_spans(text: str, name: str) -> list[tuple[int, int]]:
    spans = []
    needle = "{{" + name
    i = 0
    while True:
        start = text.find(needle, i)
        if start == -1:
            break
        after = text[start + len(needle): start + len(needle) + 1]
        if after not in ("|", "}"):
            i = start + len(needle)
            continue
        depth = 0
        j = start
        while j < len(text):
            if text[j:j + 2] == "{{":
                depth += 1
                j += 2
            elif text[j:j + 2] == "}}":
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        spans.append((start, j))
        i = j
    return spans


def expand_template_live(edition: str, title: str, wikitext: str) -> str:
    params = {
        "action": "expandtemplates",
        "format": "json",
        "formatversion": "2",
        "prop": "wikitext",
        "title": title,
        "text": wikitext,
    }
    url = f"https://{edition}.wiktionary.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    data = json.loads(open_with_retry(req).decode("utf-8"))
    return data["expandtemplates"]["wikitext"]


def replace_live_template_calls(edition: str, word: str, page_text: str, name: str) -> str:
    """Pre-expand every `{{name|...}}` call in page_text via the live API
    before local parsing even starts (see expand_template_live)."""
    spans = find_template_call_spans(page_text, name)
    for start, end in reversed(spans):
        expanded = expand_template_live(edition, word, page_text[start:end])
        page_text = page_text[:start] + expanded + page_text[end:]
    return page_text


def find_template_names(text: str) -> set[str]:
    names = set()
    for m in TEMPLATE_CALL_RE.finditer(text):
        name = m.group(1).strip()
        if not name:
            continue
        if name.lower().startswith("#invoke:"):
            module = name.split(":", 1)[1].split("|", 1)[0].strip()
            if module:
                names.add(f"Module:{module}")
        elif not name.startswith("#"):
            names.add(name if ":" in name else f"Template:{name}")
    return names


def prefetch_templates(edition: str, text: str, cache: PostgresCache, max_workers: int = 8) -> None:
    missing = [name for name in find_template_names(
        text) if cache.get(edition, name) is None]
    if not missing:
        return
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(fetch_raw_wikitext, edition, name): name
            for name in missing
        }
        for future in as_completed(futures):
            name = futures[future]
            body = future.result()
            if body is not None:
                cache.set(edition, name, body)


def load_or_fetch(edition: str, title: str, cache: PostgresCache) -> str | None:
    """Fetch+cache the literal raw wikitext for one title (no redirect following)."""
    cached = cache.get(edition, title)
    if cached is not None:
        return cached
    text = fetch_raw_wikitext(edition, title)
    if text is not None:
        cache.set(edition, title, text)
    return text


def resolve_redirect_target(edition: str, title: str, cache: PostgresCache, _chain: set[str] | None = None) -> tuple[str, str] | None:
    """Follow #REDIRECT chains to the final non-redirect (title, body) pair."""
    text = load_or_fetch(edition, title, cache)
    if text is None:
        return None
    m = REDIRECT_RE.match(text)
    if not m:
        return title, text
    target = m.group(1).strip()
    chain = _chain or set()
    if target in chain:
        return None  # redirect loop
    chain.add(target)
    return resolve_redirect_target(edition, target, cache, chain)


_loader_registry: dict[Wtp, tuple[str, PostgresCache]] = {}
_loader_registry_lock = threading.Lock()


def install_live_loader(edition: str, ctx: Wtp, cache: PostgresCache) -> None:
    """Fetch Template:/Module: pages live, the instant template expansion or
    Lua's require() actually asks for one missing, instead of needing the
    whole page pre-loaded like a dump-based run would. Catches even names
    Lua builds at runtime (e.g. "Module:table/" .. k), which a text scan
    over the page upfront could never predict.

    Wtp uses __slots__, so an instance can't hold its own callback: the
    patch is applied once, globally, and looks up each instance's
    (edition, cache) via _loader_registry. Concurrent requests, each
    with their own Wtp, don't mess up each other's settings. Pair with
    cleanup_live_loader once done with `ctx`.
    """
    with _loader_registry_lock:
        _loader_registry[ctx] = (edition, cache)

    if getattr(Wtp, "_live_loader_installed", False):
        return
    Wtp._live_loader_installed = True
    original = Wtp.get_page_resolve_redirect

    def fully_qualified(ctx: Wtp, title: str, namespace_id: int | None) -> str:
        # Templates arrive as a bare name + separate namespace_id; modules
        # arrive already prefixed (e.g. "Module:table"). The live fetch
        # needs the prefixed form either way.
        local_ns_name = namespace_id and ctx.LOCAL_NS_NAME_BY_ID.get(
            namespace_id)
        if not local_ns_name or title.startswith(local_ns_name + ":"):
            return title
        return f"{local_ns_name}:{title}"

    def bare_name(ctx: Wtp, title: str, namespace_id: int | None) -> str:
        local_ns_name = namespace_id and ctx.LOCAL_NS_NAME_BY_ID.get(
            namespace_id)
        if local_ns_name and title.lower().startswith(local_ns_name.lower() + ":"):
            return title[len(local_ns_name) + 1:]
        return title

    def ensure_registered(ctx: Wtp, edition: str, cache: PostgresCache, title: str, namespace_id: int | None) -> None:
        if original(ctx, title, namespace_id) is not None:
            return
        fetch_title = fully_qualified(ctx, title, namespace_id)
        text = load_or_fetch(edition, fetch_title, cache)
        if text is None:
            return  # genuinely missing; let normal "doesn't exist" handling apply
        store_title = title.replace("_", " ")
        if REDIRECT_RE.match(text):
            resolved = resolve_redirect_target(edition, fetch_title, cache)
            if resolved is None:
                return
            target_title, target_text = resolved
            target_model = "Scribunto" if target_title.lower().startswith(
                "module:") else "wikitext"
            ctx.add_page(bare_name(ctx, target_title, namespace_id).replace("_", " "), namespace_id,
                         body=target_text, model=target_model)
            ctx.add_page(store_title, namespace_id, redirect_to=target_title)
        else:
            model = "Scribunto" if fetch_title.startswith(
                "Module:") else "wikitext"
            ctx.add_page(store_title, namespace_id, body=text, model=model)
        ctx.get_page.cache_clear()

    def patched(self, title: str, namespace_id: int | None):
        edition, cache = _loader_registry[self]
        ensure_registered(self, edition, cache, title, namespace_id)
        return original(self, title, namespace_id)

    Wtp.get_page_resolve_redirect = patched


def cleanup_live_loader(ctx: Wtp) -> None:
    with _loader_registry_lock:
        _loader_registry.pop(ctx, None)


def lookup_word(word: str, edition: str, language_codes: list[str] | None = None, cache: PostgresCache | None = None) -> list[dict] | None:
    """Fetch+extract `word` from <edition>.wiktionary.org. 
    Returns None if the page doesn't exist. 
    `cache` defaults to a new build_cache() call if not given"""
    if edition != "en":
        raise ValueError(
            f"Unsupported edition {edition!r}: only 'en' is supported."
        )

    page_text = fetch_raw_wikitext(edition, word)
    if page_text is None:
        return None

    for lang_code in language_codes or []:
        page_text = replace_live_template_calls(
            edition, word, page_text, f"{lang_code}-conj")

    if cache is None:
        cache = build_cache()
    wtp = Wtp(lang_code=edition)
    config = WiktionaryConfig(capture_language_codes=language_codes)
    wxr = WiktextractContext(wtp, config)

    prefetch_text = (
        keep_only_requested_language_sections(wxr, page_text)
        if language_codes
        else page_text
    )
    prefetch_templates(edition, prefetch_text, cache)

    install_live_loader(edition, wtp, cache)
    init_interwiki_map(wtp)

    try:
        with contextlib.redirect_stdout(sys.stderr):
            return parse_page(wxr, word, page_text)
    finally:
        cleanup_live_loader(wtp)
