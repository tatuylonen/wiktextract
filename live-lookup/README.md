# live-lookup

Live, single-word Wiktionary extraction — fetches one word's wikitext directly
from en.wiktionary.org and runs wiktextract's own parser against just that
page, instead of processing the full XML/JSONL dump. Templates and Lua modules
it references are fetched lazily and cached in Postgres.

Only the `en` edition is supported for now, so essentially we always get the
english translation for a given word.

## Setup

```bash
cp .env.example .env   # adjust if needed
docker compose up -d
```

This starts the Postgres cache (`cache-db`) and the API (`lookup-api`,
published on `:8001`).

## API

- `GET /lookup/{word}?lang=it&lang=es` — fetch `word` from en.wiktionary.org
  and return wiktextract's raw entries, filtered to the given language
  code(s). 404 if the page doesn't exist.
- `GET /search/{query}?limit=10` — title-prefix suggestions from MediaWiki's
  own `opensearch`, for use as a "did you mean" fallback when `/lookup` finds
  nothing. Always returns a (possibly empty) list, never 404.

## Local development (without Docker)

```bash
pip install -e "..[live-lookup,live-lookup-api]"
docker compose up -d cache-db   # cache db only
export DATABASE_URL=postgresql://wiktionary_cache:wiktionary_cache@localhost:5433/wiktionary_cache
uvicorn api:app --reload
```
