"""Generate a simple html page to visualize which attributes are in which
language.

Internally, it just compares the json schemas made from Pydantic (so no English
edition!).
"""

import json
from pathlib import Path
from typing import Any, TypedDict

from generate_schema import iter_schemas

Attr = tuple[str, str]
"""A path attribute and a type. Ex. (sense.tags, array)"""
Attrs = list[Attr]


class Summary(TypedDict):
    language: str
    attributes: Attrs


def summarize_schema(schema: Any) -> Summary:
    lang = schema.get("title") or schema.get("$id") or "unknown"
    lang = lang.split()[0]

    attrs: dict[str, str] = {}  # path > type
    seen = set()

    def detect_type(node: Any) -> str:
        t = node.get("type")

        if isinstance(t, list):
            return "|".join(t)
        if isinstance(t, str):
            return t

        if "properties" in node:
            return "object"
        if "items" in node:
            return "array"

        return "unknown"

    def record(path: str, node: dict):
        if path not in attrs:
            attrs[path] = detect_type(node)

    def walk(node, prefix=""):
        if not isinstance(node, dict):
            return

        node_id = id(node)
        if node_id in seen:
            return
        seen.add(node_id)

        # Normal properties
        if "properties" in node:
            for prop, sub in node["properties"].items():
                path = f"{prefix}.{prop}" if prefix else prop
                record(path, sub)
                walk(sub, path)

        # Array items
        if node.get("type") == "array":
            items = node.get("items")
            if isinstance(items, dict):
                # array node itself may also be a property
                if prefix and prefix not in attrs:
                    record(prefix, node)
                walk(items, prefix)

        # Definitions
        if "$defs" in node:
            for defname, defschema in node["$defs"].items():
                path = f"$defs.{defname}"
                record(path, defschema)
                walk(defschema, path)

        # Combinators
        for key in ("oneOf", "anyOf", "allOf"):
            if key in node:
                for sub in node[key]:
                    walk(sub, prefix)

        # $ref
        if "$ref" in node:
            ref = node["$ref"]
            if ref.startswith("#/"):
                target = schema
                for part in ref[2:].split("/"):
                    target = target.get(part, {})
                walk(target, prefix)

    walk(schema)

    # Convert to list of (path, type)
    attributes: Attrs = sorted(attrs.items())

    return {
        "language": lang,
        "attributes": attributes,
    }


def read_all_summaries() -> dict[str, Attrs]:
    summaries = {}

    for _, model_schema in iter_schemas():
        # Seems dumb, but we need this to replicate reading the schemas from
        # the _site folder, due to key sorting...
        schema = json.loads(
            json.dumps(
                model_schema,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        summary = summarize_schema(schema)
        lang = summary["language"]
        summaries[lang] = summary["attributes"]

    return summaries


def add_summary_to_tree(global_tree: dict, lang: str, attrs: Attrs) -> None:
    """Convert the flat attrs to dictionary tree.

    Each node gets a _langs set that accumulates languages reaching it.
    """
    for path, ty in attrs:
        node = global_tree
        for p in path.split("."):
            node = node.setdefault(p, {})
            node.setdefault("_langs", set()).add(lang)
            node.setdefault("_type", set()).add(ty)


def basic_css() -> str:
    return """
<style>
.all  { color: green; }
.one  { color: red; }
.some { color: black; }

/* Yoinked @
https://gist.githubusercontent.com/dylancwood/7368914/raw/48a6e93ab59a1017ee6a8512a2bf5be343aa307c/tree.css
*/

ul.tree,
ul.tree ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

ul.tree ul {
    margin-left: 20px; /* Changed this to be bigger */
}

ul.tree li {
    margin: 0;
    padding: 0 7px;
    line-height: 20px;
    color: #369;
    font-weight: bold;
    border-left: 1px solid rgb(100, 100, 100);
}

ul.tree li:last-child {
    border-left: none;
}

ul.tree li:before {
    position: relative;
    top: -0.3em;
    height: 1em;
    width: 12px;
    color: white;
    border-bottom: 1px solid rgb(100, 100, 100);
    content: "";
    display: inline-block;
    left: -7px;
}

ul.tree li:last-child:before {
    border-left: 1px solid rgb(100, 100, 100);
}

</style>
"""


def html_tree(tree: dict, all_langs: list[str]) -> str:
    """Return HTML for the tree; languages visible on hover. No CSS."""
    from html import escape

    n_langs = len(all_langs)
    all_langs_set = set(all_langs)

    def go(node: dict) -> str:
        parts = ['<ul class="tree">']

        for key, child in sorted(node.items()):
            if not isinstance(child, dict):
                continue

            langs = child.get("_langs", set())
            assert langs, "langs should not be empty"
            missing = all_langs_set - langs
            present = langs
            missing_in = ", ".join(sorted(missing))
            present_in = ", ".join(sorted(present))
            tooltip = f"Present in: {present_in}\nMissing in: {missing_in}"

            count = len(langs)
            if count == n_langs:
                count_cls = "all"
            elif count == 1:
                count_cls = "one"
                first_lang = list(langs)[0]
                count = f"1, {first_lang}"
            else:
                count_cls = "some"

            is_leaf = not any(isinstance(v, dict) for v in child.values())
            types = child.get("_type", set())
            types_info = ""
            if is_leaf and len(types) > 1:
                type_list = ", ".join(sorted(types))
                types_info = f' <span title="{escape(type_list)}">⚠️</span>'

            key = escape(key)
            label = (
                f'<span class="{count_cls}">{key} ({count}){types_info}</span>'
            )

            parts.append(f'<li title="{tooltip}">{label}')
            parts.append(go(child))
            parts.append("</li>")

        parts.append("</ul>")
        return "".join(parts)

    return go(tree)


def main() -> None:
    summaries = read_all_summaries()

    langs = sorted(summaries.keys())

    global_tree = {}
    for lang, attrs in summaries.items():
        add_summary_to_tree(global_tree, lang, attrs)

    output_path = Path("_summary")
    output_path.mkdir(exist_ok=True)
    summary_path = output_path / "summary.html"
    with summary_path.open("w") as f:
        page = basic_css() + html_tree(global_tree, langs)
        f.write(page)

    print(f"Wrote summary @ {summary_path}")


if __name__ == "__main__":
    main()
