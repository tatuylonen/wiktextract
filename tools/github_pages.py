import json
from pathlib import Path


def main():
    """
    Generate a simple HTML page to list files in the `_site` folder.
    """
    html = """
    <!DOCTYPE HTML>
    <html lang="en-US">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width" />
            <title>wiktextract</title>
        </head>
        <body>
            <h1>wiktextract</h1>
            <h2><a href="htmlcov/index.html">Coverage report</a></h2>
            <h2>JSON schema</h2>
            <ul>
            <schema_list>
            </ul>
        </body>
    </html>
    """

    schema_paths = [
        path
        for path in Path("_site").iterdir()
        if path.is_file() and path.suffix == ".json"
    ]
    schema_paths.sort(key=lambda p: p.name)
    schema_list_html = ""
    for schema_path in schema_paths:
        with schema_path.open(encoding="utf-8") as f:
            schema_data = json.load(f)
            schema_list_html += f"<li><a href='{schema_path.name}'>{schema_data.get('title')}</a></li>"
    html = html.replace("<schema_list>", schema_list_html)
    with open("_site/index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
