import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path


def worker(line, schema={}):
    from jsonschema import validate

    validate(instance=json.loads(line), schema=schema)


def main():
    """
    Validate extracted JSONL file with JSON schema.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl_path", type=Path)
    parser.add_argument("schema_path", type=Path)
    args = parser.parse_args()

    with (
        args.jsonl_path.open(encoding="utf-8") as jsonl_f,
        args.schema_path.open(encoding="utf-8") as schema_f,
        ProcessPoolExecutor() as executor,
    ):
        schema = json.load(schema_f)
        for _ in executor.map(
            partial(worker, schema=schema), jsonl_f, chunksize=1000
        ):
            pass


if __name__ == "__main__":
    main()
