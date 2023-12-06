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
    """

    json_schemas = [
        path.name
        for path in Path("_site").iterdir()
        if path.is_file() and path.suffix == ".json"
    ]
    json_schemas.sort()
    for schema in json_schemas:
        html += f"<li><a href='{schema}'>{schema}</a></li>"

    html += """
        </ul>
        </body>
    </html>
    """

    with open("_site/index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
