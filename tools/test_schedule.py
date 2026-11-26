import os
import sys
from datetime import datetime

import requests


def get(url: str) -> dict:
    # Unauthenticated calls share the runner's 60 requests an hour, so send
    # the job's token when the workflow passes it. A failed call raises with
    # its status instead of a KeyError on the missing field.
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def main() -> int:
    """
    This code runs daily to trigger test action then update container image if
    wikitextprocessor's code is newer than the version used in the latest test.

    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-workflow
    """

    runs = get(
        "https://api.github.com/repos/tatuylonen/wiktextract/actions/workflows/59463306/runs?branch=master&per_page=20"
    )["workflow_runs"]
    # Every run of this workflow starts a test run, which is skipped when
    # this returns 1. A skipped run tested nothing, so it doesn't count.
    tested = [run for run in runs if run["conclusion"] != "skipped"]
    if not tested:
        print("no test run in the last 20 runs")
        return 0
    latest_test = datetime.fromisoformat(tested[0]["created_at"])
    latest_wikitextprocessor_commit = datetime.fromisoformat(
        get(
            "https://api.github.com/repos/tatuylonen/wikitextprocessor/commits/main"
        )["commit"]["committer"]["date"]
    )
    print(f"latest test run: {latest_test}")
    print(
        f"latest wikitextprocessor commit: {latest_wikitextprocessor_commit}"
    )
    if latest_test < latest_wikitextprocessor_commit:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
