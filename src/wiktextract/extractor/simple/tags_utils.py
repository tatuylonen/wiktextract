import re

from .simple_tags import simple_tag_map

# If you want to use groups in a regex meant for re.split(), you need to use the
# syntax `(?:...)` to make the group non-capturing. re.split() has the feature
# of outputting captured "splitters" if they're in a `(group)`, which is very
# handy but not relevant here; we don't need to keep that data.
SPLITTER_RE = re.compile(r"\s*(?:,|;|\(|\)|\.)\s*")

def convert_tags(raw_tags: list[str]) -> tuple[list[str], list[str]]:
    """Check if raw tags contain tag strings in `simple_tag_map` and return
    two lists of strings, the newly extract tags and the remaining raw tags.
    """
    tags = []
    new_raw_tags = []
    for tag in raw_tags:
        ttags = []
        rtags = []
        for s in SPLITTER_RE.split(tag):
            s = s.strip(" \n\t,;.:#*-–")
            if not s:
                continue
            if s in simple_tag_map:
                ttags.extend(simple_tag_map[s])
            else:
                rtags.append(s)
        if len(ttags) > 0:
            tags.extend(ttags)
            new_raw_tags.extend(rtags)
        else:
            new_raw_tags.append(tag.strip())

    if len(tags) > 0:
        return tags, new_raw_tags

    return [], raw_tags
