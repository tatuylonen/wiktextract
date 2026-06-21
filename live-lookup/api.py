"""
FastAPI wrapper around lookup.py's lookup_word().
uvicorn api:app --reload
"""

from fastapi import FastAPI, HTTPException, Query
from cache import build_cache
from lookup import lookup_word, mediawiki_opensearch

EDITION = "en"  # for now only en is supported
app = FastAPI(title="live-lookup")
cache = build_cache()


@app.get("/lookup/{word}")
def lookup(word: str, lang: list[str] | None = Query(default=None)):
    """ lookup the english translation of a word, which can be in any of the given lang's
    (e.g. /lookup/casa?lang=it&lang=es)"""
    results = lookup_word(word, EDITION, lang, cache=cache)
    if results is None:
        raise HTTPException(
            status_code=404, detail=f"No page found for {word!r}"
        )
    return results


@app.get("/search/{query}")
def search(query: str, limit: int = 10):
    """ suggestions fallback if lookup returns nothing """
    return mediawiki_opensearch(EDITION, query, limit)
