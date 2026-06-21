import os
import sys


class PostgresCache:
    def __init__(self, database_url: str):
        import psycopg2

        self.conn = psycopg2.connect(database_url)
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS page_cache (
                    edition TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    PRIMARY KEY (edition, title)
                )
                """
            )

    def get(self, edition: str, title: str) -> str | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT body FROM page_cache WHERE edition = %s AND title = %s",
                (edition, title),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def set(self, edition: str, title: str, body: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO page_cache (edition, title, body)
                VALUES (%s, %s, %s)
                ON CONFLICT (edition, title)
                DO UPDATE SET body = EXCLUDED.body, fetched_at = now()
                """,
                (edition, title, body),
            )


def build_cache() -> PostgresCache:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(
            "DATABASE_URL is not set. Start the cache db (docker compose up -d) "
            "and set DATABASE_URL. Create an .env file with the variables set like .env.example.",
            file=sys.stderr,
        )
        sys.exit(1)
    return PostgresCache(database_url)
