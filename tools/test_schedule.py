import sys
from datetime import datetime

import requests


def main() -> int:
    """
    This code runs daily to trigger test action then update container image if
    wikitextprocessor's code is newer than the version used in the latest test.

    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-workflow
    """

    r = requests.get(
        "https://api.github.com/repos/tatuylonen/wiktextract/actions/workflows/59463306/runs?branch=master&per_page=1"
    )
    latest_test = datetime.fromisoformat(
        r.json()["workflow_runs"][0]["created_at"]
    )
    r = requests.get(
        "https://api.github.com/repos/tatuylonen/wikitextprocessor/commits/main"
    )
    latest_wikitextprocessor_commit = datetime.fromisoformat(
        r.json()["commit"]["committer"]["date"]
    )
    if latest_test < latest_wikitextprocessor_commit:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
