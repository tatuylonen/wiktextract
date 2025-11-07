import re

from .models import Sense
from .section_titles import POS_HEADINGS
from .text_utils import ENDING_NUMBER_RE, STRIP_PUNCTUATION, normalized_int

# If you want to use groups in a regex meant for re.split(), you need to use the
# syntax `(?:...)` to make the group non-capturing. re.split() has the feature
# of outputting captured "splitters" if they're in a `(group)`, which is very
# handy but not relevant here; we don't need to keep that data.
SPLITTER_RE = re.compile(r"\s*(?:,|;|\(|\)|\.|&)\s*")


def convert_tags(raw_tags: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Return lists of strings: tags, raw_tags and parts of speech.

    Note that the translation raw_tags > tags is done elsewhere for Senses.
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
            heading_posmap = POS_HEADINGS.get(s.lower())
            if heading_posmap is not None:
                # XXX might be better to separate out the POS-number here
                pos = heading_posmap["pos"]
                if pos_num and pos_num != -1:
                    pos = f"{pos} {pos_num}"
                pposes.append(pos)
                if heading_tags := heading_posmap.get("tags"):
                    ttags.extend(heading_tags)
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
    # While this is generally useful, it can also miss because these poses may
    # not refer to the sense:
    #   https://el.wiktionary.org/wiki/Ινδός
    #   where (θηλυκό Ινδή) does not claim that the Sense is feminine
    #   but that the feminine version of Ινδός is Ινδή
    #
    # ... but then there should not have been in raw.tags? and parsed into a
    # Form before reaching this?
    sense.tags.extend(poses)
