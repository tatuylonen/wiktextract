# Implements very basic disambiguation of translations and linkages, mostly
# for trivial and unambiguous cases.  It is expected that a more powerful
# heuristic disambiguator would be used as a separate step to finish the
# disambiguation.
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org.

import collections
from wikitextprocessor import Wtp
from .datautils import data_append, data_extend

def clean_item_sense(text):
    # Cleans up some aspects of a word sense or gloss before comparison
    # (this is helper function for disambiguate_clear_cases())
    assert isinstance(text, str)
    text = text.lower()
    if text.endswith("."):
        text = text[:-1]
    if text.startswith("slang: "):
        text = text[7:]
    return text.strip()

def disambiguate_clear_cases(ctx, data, field):
    # After parsing a part-of-speech, move those data items in the
    # given field fields for which there is no ambiguity to their
    # respective senses.  Assumes the data items have a "sense" field.
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(field, str)

    if field not in data:
        return
    items = collections.defaultdict(list)
    for item in data[field]:
        sensetext = item.get("sense", "")
        sensetext = clean_item_sense(sensetext)
        items[sensetext].append(item)
    del data[field]

    senses_with_no_items = []
    for sense in data.get("senses", ()):
        for gloss in sense.get("glosses", ()):
            gloss = clean_item_sense(gloss)
            for k, v in items.items():
                if k == "":
                    continue
                if (gloss == k or
                    gloss == "a " + k or
                    gloss == "an " + k or
                    gloss.startswith("a " + k + " ") or
                    gloss.startswith("an " + k + " ") or
                    gloss.startswith(k + ",") or
                    gloss.startswith(k + ".") or
                    gloss.startswith(k + " or ")):
                    data_extend(ctx, sense, field, v)
                    del items[k]
                    break
            else:
                continue
            break
        else:
            senses_with_no_items.append(sense)

    # Any remaining items go to those senses that did not have any
    # items.  When there is ambiguity, the item is left at
    # word-level.
    if (len(senses_with_no_items) == 1 and
        len(list(items)) == 1):
        sense = senses_with_no_items[0]
        for k, v in items.items():
            data_extend(ctx, sense, field, v)
        return

    # Leave any items that we couldn't assign to the original data
    if items:
        for k, v in items.items():
            data_extend(ctx, data, field, v)
