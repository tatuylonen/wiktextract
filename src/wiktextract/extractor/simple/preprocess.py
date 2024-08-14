from .parse_utils import PANEL_TEMPLATES
from .section_titles import POS_DATA
from .text_utils import (
    HEADING_RE,
    POS_STARTS_RE,
    POS_TEMPLATE_NAMES,
    SECTION_STARTERS,
    TEMPLATE_NAME_RE,
)


def preprocess_text(text: str, page_title="") -> str:
    """Use simple text processing to rearrange the hierarchy of the page so that
    sections like `Word part` and `Pronunciation` will start a new main section.
    We do this by introducing LEVEL 1 headings, with a dummy title."""

    Section = tuple[str, int, list[str]]
    parts: list[Section] = []
    cur_part: Section = ("TOP_LEVEL", 0, [])
    # Does a POS template have a preceding POS heading; whitespace and
    # other POS templates are allowed between
    after_pos_heading = False

    for line in text.splitlines():
        if line.startswith("=") and line.endswith("="):
            heading = HEADING_RE.match(line)
            if heading is not None:
                if POS_STARTS_RE.match(heading.group(2)):
                # This heading is for a POS section
                    after_pos_heading = True
                # Start a new heading part
                parts.append(cur_part)
                # if we encounter a level 1 node ("="), demote to level 2
                if (depth := len(heading.group(1))) == 1:
                    depth = 2
                cur_part = (heading.group(2), depth, [])
        elif line.startswith("{{") and line.endswith("}}"):
            # Check if a POS template is preceded by a POS heading
            if not after_pos_heading:
                m = TEMPLATE_NAME_RE.match(line.strip())
                if m and m.group(1) in POS_TEMPLATE_NAMES:
                    # print(f"///// found "broken" article in '{page_title}'")
                    # print(f"///// {m.group(0)}")
                    # print(text)
                    parts.append(cur_part)
                    pos_title = ""
                    # Get a heading title in reverse from POS_DATA
                    # XXX in the future, template names might overlap between
                    # different heading titles, so this should be made more
                    # correct
                    for k, v in POS_DATA.items():
                        if m.group(1) in v.get("templates", ()):
                            pos_title = k
                            break
                    # Add a virtual heading here
                    cur_part = (pos_title or m.group(1), 2, [])
                elif m and m.group(1) in PANEL_TEMPLATES:
                    # do nothing, ignore line
                    pass
                # Not a POS template, not ignorable template
                else:
                    after_pos_heading = False
        else:
            # Content other than whitespace
            if line.strip():
                after_pos_heading = False

        # We mainly insert extra headings before the 'current' line in
        # the above code, so ATM it's easy to just append lines by default.
        cur_part[2].append(line)
    # Sentinel append for the last cur_part
    parts.append(cur_part)

    # for pline in parts:
    #     print(pline)

    # We use MAGIC_SECTION level-1 headings to split the article
    ret = [
        "= MAGIC_SECTION =",
    ]

    inside_pos = False

    for i, part in enumerate(parts):
        if part[0].lower() in SECTION_STARTERS and inside_pos:
            if any(
                x[1] == 2 and x[0].lower() not in SECTION_STARTERS
                for x in parts[i + 1 :]
            ):
                inside_pos = False
                ret.append("= MAGIC_SECTION =")
        if part[1] == 2 and part[0].lower() not in SECTION_STARTERS:
            inside_pos = True
        # Output all level 2 headings that aren't POSes to level 3
        if (
            part[1] == 2  # == Heading ==
            and part[0].lower() not in POS_DATA  # == Not a POS? ==
            and not (
                part[0].endswith(
                    ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
                )  #  not == Heading 2 ==
                and POS_STARTS_RE.match(part[0])  #  not == Noun 2 ==
            )
        ):
            ret.append(f"=== {part[0]} ===")
            ret.extend(part[2][1:])
            continue
        ret.extend(part[2])

    return "\n".join(ret)
