import re

from .models import Sense
from .section_titles import POS_HEADINGS
from .simple_tags import simple_tag_map
from .text_utils import ENDING_NUMBER_RE, STRIP_PUNCTUATION, normalized_int

# If you want to use groups in a regex meant for re.split(), you need to use the
# syntax `(?:...)` to make the group non-capturing. re.split() has the feature
# of outputting captured "splitters" if they're in a `(group)`, which is very
# handy but not relevant here; we don't need to keep that data.
SPLITTER_RE = re.compile(r"\s*(?:,|;|\(|\)|\.|&)\s*")


def convert_tags(raw_tags: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Check if raw tags contain tag strings in `simple_tag_map` and return
    lists of strings: tags, raw_tags and parts of speech.
    """

    if not any(s.strip(STRIP_PUNCTUATION) for s in raw_tags):
        return [], [], []

    tags = []
    new_raw_tags = []
    # Parts-of-speech-es
    poses = []
    for tag in raw_tags:
        if not tag.strip():
            continue
        ttags = []
        rtags = []
        pposes = []
        for s in SPLITTER_RE.split(tag):
            s = s.strip(STRIP_PUNCTUATION)
            if not s:
                continue
            pos = ""
            pos_num = -1
            if m := ENDING_NUMBER_RE.search(s):
                s = s[: m.start()].strip()
                pos_num = normalized_int(m.group(1))
            if s.lower() in POS_HEADINGS:
                # XXX might be better to separate out the POS-number here
                if pos_num and pos_num != -1:
                    pos = f"{s.lower()} {pos_num}"
                else:
                    pos = s.lower()
                pposes.append(pos)
            elif s in simple_tag_map:
                ttags.extend(simple_tag_map[s])
            else:
                rtags.append(s)
        if len(ttags) > 0 or len(pposes) > 0:
            tags.extend(ttags)
            poses.extend(pposes)
            new_raw_tags.extend(rtags)
        else:
            new_raw_tags.append(tag.strip(STRIP_PUNCTUATION))

    if len(tags) > 0 or len(poses) > 0:
        return tags, new_raw_tags, poses

    return [], [s.strip(STRIP_PUNCTUATION) for s in raw_tags], []


def convert_tags_in_sense(sense: Sense) -> None:
    tags, raw_tags, poses = convert_tags(sense.raw_tags)
    sense.tags.extend(tags)
    sense.raw_tags = raw_tags
    sense.tags.extend(poses)
