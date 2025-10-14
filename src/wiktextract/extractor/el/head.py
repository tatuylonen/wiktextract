import re
from unicodedata import name as unicode_name

from mediawiki_langcodes import code_to_name

from wiktextract.clean import clean_value
from wiktextract.extractor.en.form_descriptions import distw
from wiktextract.wxr_context import WiktextractContext

from .models import Form

BOLD_RE = re.compile(r"(__/?[BIL]__|\(|\)|, |\. |: )")


def parse_head(wxr: WiktextractContext, text: str) -> list[Form]:
    text = clean_value(wxr, text)
    split_text = BOLD_RE.split(text)
    # print(split_text)

    if not split_text[0] == "":
        # This should always be True; maybe an assert?
        # Turns out *some* articles add `-` before the template, like funa...
        if split_text[0] in ("-", "το "):
            if len(split_text) > 3:
                # Just throw the prefix into the (probably) bolded text
                split_text[2] = split_text[0] + split_text[2]
                split_text[0] = ""
            else:
                return []
        else:
            return []

    forms: list[Form] = []
    # print_blocks = []

    for form_ret in partition_head_forms(wxr, split_text):
        # print_blocks.append(form_block)
        # logger.info(f"\n  §§ {form_ret}")
        forms.append(form_ret)

    # logger.info(
    #     f"\n  §§ {wxr.wtp.title} ->  {''.join(split_text)}\n  § "
    #     + "\n  § ".join(f"{''.join(pb)}" for pb in print_blocks)
    # )
    return forms


# Sometimes bolded sections of the head are just smooshed together; what
# I've seen, it's "form -a -b -c", that is, suffixes.
SUFFIXES_RE = re.compile(r"\s+(-\w+)\b")


def partition_head_forms(
    wxr: WiktextractContext, split_text: list[str]
) -> list[Form]:
    if len(split_text) < 2:
        wxr.wtp.error(
            f"Failed to partition head forms; too few items {split_text=}",
            sortid="head/50/20250303",
        )
        return []

    Forms = list[str]
    Tags = list[str]
    blocks: list[tuple[Forms, Tags]] = [([], [])]
    current_forms: Forms = []
    current_tags: Tags = []

    def push_new_block():
        nonlocal current_forms
        nonlocal current_tags
        blocks.append((current_forms, current_tags))
        current_forms = []
        current_tags = []

    def extend_old_block():
        nonlocal current_forms
        nonlocal current_tags
        blocks[-1][0].extend(current_forms)
        blocks[-1][1].extend(current_tags)
        current_forms = []
        current_tags = []

    seen_italics = "__I__" in split_text
    seen_bold = "__B__" in split_text
    inside_parens = False
    inside_bold = False
    inside_link = False
    inside_italics = False

    previous_token_was_period = False
    for i, t in enumerate(split_text):
        # print(f"{i}: {t=}")
        # print(f"{current_forms=}, {current_tags=}. Now: {t=}")
        t2 = t.strip()
        if not t2 and t and previous_token_was_period:
            # Whitespace
            # print("Prev. was dot")
            previous_token_was_period = False
            push_new_block()
            continue
        t = t2
        if i % 2 == 0:
            previous_token_was_period = False
        if t in ("", "ή"):
            continue
        elif t in ("και", "&", ":", ".:"):
            push_new_block()
            continue

        if i % 2 == 0:
            # Odd elements: text

            if t == ".":
                previous_token_was_period = True
                continue

            # Check if word is not in greek; if it's not, that's a form.
            # XXX this might be problematic if there's a stretch of unbolded
            # text where the bolding has just been forgotten. Fix by
            # checking each word for greekness?
            # This doesn't need to check if the language we're processing
            # is greek or not, because all non-greek words are 'forms'.
            found_language_code = False
            is_foreign_script = False
            for ch in t:
                if not ch.isalpha():
                    continue
                if not unicode_name(ch).startswith("GREEK"):
                    if code_to_name(t) != "":
                        found_language_code = True
                        break
                    is_foreign_script = True
                    break

            if found_language_code:
                break

            if inside_italics:
                # Italicized words should always be tags
                current_tags.append(t)
                continue
            if is_foreign_script:
                current_forms.append(t)
                continue
            if inside_bold:
                # Bolded words should always be forms
                # Split off any suffixes inside the same bold node.
                suffixes = SUFFIXES_RE.split(t)
                for f in suffixes:
                    f = f.strip()
                    if not f:
                        continue
                    current_forms.append(f)
                # print(f"inside_bold {t=} {current_forms=}")
                continue

            if inside_link or (
                not inside_italics and not inside_bold and not seen_bold
            ):
                # Usually a form, sometimes a tag...
                # XXX handle titles with whitespace by doing the splitting
                # in N steps: there's one space, split A B C D with
                # A B, C D and (A), B C, (D)

                if (
                    seen_italics and not seen_bold
                ):  # there has been text in italics before
                    current_forms.append(t)
                    continue
                words = t.split()
                orig_words = (wxr.wtp.title or "").split()

                if len(words) < len(orig_words):
                    # The phrase we're looking at it shorter than the article
                    # title in words; unlikely that a form like this loses
                    # words (more likely to add words) so consider this a
                    # tag: XXX if this turns out to be problematic
                    current_tags.append(t)
                    continue

                matches = 0

                for word in words:
                    if distw(orig_words, word) < 0.4:
                        matches += 1
                        break

                if matches > 0:  # XXX use better heuristic; problem is that
                    # percentage-wise, if you add two words to
                    # one word then the percentage needed is low
                    # to match it.
                    current_forms.append(t)
                    continue

                current_tags.append(t)
                continue

            continue

        # Even elements: splitter tokens like commas, parens or formatting
        match t:
            case "(":
                if current_forms and current_tags:
                    push_new_block()
                else:
                    extend_old_block()
                # We don't support nested parens; XXX if there's a problem
                # with them
                inside_parens = True
            case ")":
                inside_parens = False
                # print(f"{current_forms=}, {current_tags=}, {t=}")
                if (
                    not current_forms
                    and len(current_tags) == 1
                    and code_to_name(current_tags[0]) != ""
                ):
                    # There are a lot of `(en)` language code tags that we
                    # don't care about because they're just repeating the
                    # language code of the word entry itself!
                    current_tags = []
                    continue
                if current_forms and current_tags:
                    push_new_block()
                else:
                    extend_old_block()
            case ",":
                if not inside_parens:
                    if current_forms and current_tags:
                        push_new_block()
                    else:
                        extend_old_block()
            case ":":
                if not inside_parens:
                    # Do not append to previous. `:` should, logically,
                    # always point forward
                    push_new_block()
            case ".":
                if not inside_parens:
                    push_new_block()
            case "__B__":
                # print(f"{current_forms=}, {current_tags=}")
                if not inside_parens and current_forms and current_tags:
                    push_new_block()
                elif not inside_parens:
                    extend_old_block()
                inside_bold = True
            case "__/B__":
                inside_bold = False
            case "__L__":
                inside_link = True
            case "__/L__":
                inside_link = False
            case "__I__":
                inside_italics = True
            case "__/I__":
                inside_italics = False
            case _:
                pass
        # print(f"{t=}, {blocks=}")
    if len(current_forms) > 0 and len(current_tags) > 0:
        push_new_block()
    else:
        extend_old_block()

    ret: list[Form] = []

    for forms, tags in blocks:
        # print(f"{forms=}, {tags=}")
        tags = sorted(set(tags))

        for form in forms:
            ret.append(Form(form=form, raw_tags=tags))

    return ret
