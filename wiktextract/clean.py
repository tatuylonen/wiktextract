# This file contains code to clean Wiktionary annotations from a string and to
# produce plain text from it, typically for glossary entries but this is also
# called for various other data to produce clean strings.
#
# This file also contains code for cleaning qualifiers for the "tags" field.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import html
import unicodedata
from wikitextprocessor.common import MAGIC_FIRST, MAGIC_LAST
from .config import WiktionaryConfig

######################################################################
# Cleaning values into plain text.
######################################################################

superscript_ht = {
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "+": "⁺",
    "-": "⁻",
    "=": "⁼",
    "(": "⁽",
    ")": "⁾",
    "A": "ᴬ",
    "B": "ᴮ",
    "D": "ᴰ",
    "E": "ᴱ",
    "G": "ᴳ",
    "H": "ᴴ",
    "I": "ᴵ",
    "J": "ᴶ",
    "K": "ᴷ",
    "L": "ᴸ",
    "M": "ᴹ",
    "N": "ᴺ",
    "O": "ᴼ",
    "P": "ᴾ",
    "R": "ᴿ",
    "T": "ᵀ",
    "U": "ᵁ",
    "V": "ⱽ",
    "W": "ᵂ",
    "a": "ᵃ",
    "b": "ᵇ",
    "c": "ᶜ",
    "d": "ᵈ",
    "e": "ᵉ",
    "f": "ᶠ",
    "g": "ᵍ",
    "h": "ʰ",
    "i": "ⁱ",
    "j": "ʲ",
    "k": "ᵏ",
    "l": "ˡ",
    "m": "ᵐ",
    "n": "ⁿ",
    "o": "ᵒ",
    "p": "ᵖ",
    "r": "ʳ",
    "s": "ˢ",
    "t": "ᵗ",
    "u": "ᵘ",
    "v": "ᵛ",
    "w": "ʷ",
    "x": "ˣ",
    "y": "ʸ",
    "z": "ᶻ",
    "β": "ᵝ",
    "γ": "ᵞ",
    "δ": "ᵟ",
    "θ": "ᶿ",
    "ι": "ᶥ",
    "φ": "ᵠ",
    "χ": "ᵡ",
}

subscript_ht = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
    "+": "₊",
    "-": "₋",
    "=": "₌",
    "(": "₍",
    ")": "₎",
    "a": "ₐ",
    "e": "ₑ",
    "h": "ₕ",
    "i": "ᵢ",
    "j": "ⱼ",
    "k": "ₖ",
    "l": "ₗ",
    "m": "ₘ",
    "n": "ₙ",
    "o": "ₒ",
    "p": "ₚ",
    "r": "ᵣ",
    "s": "ₛ",
    "t": "ₜ",
    "u": "ᵤ",
    "v": "ᵥ",
    "x": "ₓ",
    "ə": "ₔ",
    "ρ": "ᵨ",
    "φ": "ᵩ",
    "χ": "ᵪ",
}

def to_superscript(text):
    "Converts text to superscript."
    if not text:
        return ""
    if all(x in superscript_ht for x in text):
        return "".join(superscript_ht[x] for x in text)
    if len(text) == 1:
        return "^" + text
    return "^({})".format(text)

def to_subscript(text):
    """Converts text to subscript."""
    if not text:
        return ""
    if all(x in subscript_ht for x in text):
        return "".join(subscript_ht[x] for x in text)
    if len(text) == 1:
        return "_" + text
    return "_({})".format(text)

def to_chem(text):
    """Converts text to chemical formula, making digits subscript."""
    return "".join(to_subscript(x) if x.isdigit() else x
                   for x in text)

math_map = {
    "ldots": "…",
    "textbar": "|",
    "textbullet": "•",
    "textbackslash": "\\",
    "S": "§",
    "textless": "<",
    "textgreater": ">",
    "sim": "∼",
    "tiny": "",
    "scriptsize": "",
    "footnotesize": "",
    "small": "",
    "normalsize": "",
    "large": "",
    "leq": "≤",
    "geq": "≥",
    "neq": "≠",
    "doteq": "≐",
    "approx": "≈",
    "times": "⨯",
    "div": "÷",
    "pm": "±",
    "mp": "∓",
    "cdot": "·",
    "circ": "∘",
    "ast": "∗",
    "smallsetminus": "∖",
    "slash": "∕",
    "prime": "′",
    "second": "′′",
    "third": "′′′",
    "fourth": "′′′′",
    "backprime": "‵",
    "dagger": "†",
    "ddagger": "‡",
    "ldots": "...",
    "cat": "⁀",
    "cdots": "⋯",
    "infty": "∞",
    "neg": "¬",
    "wedge": "∧",
    "vee": "∨",
    "forall": "∀",
    "in": "∈",
    "ni": "∋",
    "nni": "∌",
    "rightarrow": "→",
    "leftarrow": "←",
    "subset": "⊂",
    "subseteq": "⊆",
    "supset": "⊃",
    "supseteq": "⊇",
    "prec": "≺",
    "succ": "≻",
    "exists": "∃",
    "nexists": "∄",
    "notin": "∉",
    "Rightarrow": "⇒",
    "Leftarrow": "⇐",
    "cup": "∪",
    "cap": "∩",
    "mid": "∣",
    "nmid": "∤",
    "parallel": "∥",
    "nparallel": "∦",
    "rightangle": "∟",
    "angle": "∠",
    "measuredangle": "∡",
    "sphericalangle": "∢",
    "propto": "∝",
    "Leftrightarrow": "⇔",
    "vdots": "⋮",
    "diameter": "∅",
    "lceil": "⌈",
    "rceil": "⌉",
    "lfloor": "⌊",
    "rfloor": "⌋",
    "varnothing": "∅",
    "sptilde": "~",
    "cent": "¢",
    "pounds": "£",
    "yen": "¥",
    "lbrack": "[",
    "backslash": "\\",
    "rbrack": "]",
    "sphat": "^",
    "Micro": "μ",
    "eth": "ð",
    "imath": "ı",
    "jmath": "ȷ",

    "alpha": "𝛼",
    "beta": "𝛽",
    "varbeta": "β",
    "gamma": "𝛾",
    "delta": "𝛿",
    "epsilon": "𝜀",
    "varepsilon": "ε",
    "zeta": "𝜁",
    "eta": "𝜂",
    "theta": "𝜃",
    "vartheta": "θ",
    "iota": "𝜄",
    "kappa": "𝜅",
    "lambda": "𝜆",
    "mu": "𝜇",
    "nu": "𝜈",
    "xi": "𝜉",
    "pi": "𝜋",
    "rho": "𝜌",
    "sigma": "𝜎",
    "varsigma": "ς",
    "tau": "𝜏",
    "upsilon": "𝜐",
    "phi": "𝜑",
    "chi": "𝜒",
    "psi": "𝜓",
    "omega": "𝜔",
    "Gamma": "𝛤",
    "Delta": "𝛥",
    "Theta": "𝛩",
    "Lambda": "𝛬",
    "Xi": "𝛯",
    "Pi": "𝛱",
    "Sigma": "𝛴",
    "Upsilon": "𝛶",
    "Phi": "𝛷",
    "Psi": "𝛹",
    "Omega": "𝛺",
    "nabla": "∇",
    "partial": "∂",
    "int": "∫",
    "iint": "∫∫",
    "iint": "∫∫∫",
    "oint": "∮",
    "oiint": "∮∮",
    "Euler": "Ɛ",
    "Im": "ℑ",
    "ell": "ℓ",
    "wp": "℘",
    "Re": "ℜ",
    "tcohm": "Ω",
    "mho": "℧",
    "Angstroem": "Å",
    "Finv": "Ⅎ",
    "aleph": "א",
    "beth": "ב",
    "gimel": "ג",
    "daleth": "ד",
    "Yup": "⅄",
    "complement": "∁",
    "dotplus": "∔",

    "grave": "̀",
    "acute": "́",
    "hat": "̂",
    "tilde": "̃",
    "bar": "̄",
    "breve": "̆",
    "dot": "̇",
    "ddot": "̈",
    "mathring": "̊",
    "check": "̌",
    "not": "̸",

    "textstyle": "",
    "mathcal": "MATHCAL",  # XXX
    "mathfrak": "MATHFRAK",  # XXX
    "mathbb": "MATHBB",  # XXX
    "sqrt": "√",  # ∛ ∜
    "frac": " / ",
    "sum": "∑",
    "prod": "∏",
    "coprod": "∐",
    "lvec": "⃐",
    "vec": "⃑",
}

def to_math(text):
    """Converts a mathematical formula to ASCII."""
    magic_vec = []

    def math_magic(text, left, right, fn):
        regexp = r"{}([^{}{}]){}".format(
            re.escape(left), re.escape(left),
            re.escape(right), re.escape(right))
        regexp = re.compile(regexp)

        def repl(m):
            magic = chr(MAGIC_FIRST + len(magic_vec))
            t = fn(m.group(1))
            magic_vec.append(t)
            return magic

        while True:
            orig = text
            text = re.sub(regexp, repl, text)
            if text == orig:
                break
        return text

    parts = []
    text = math_magic(text, "{", "}", to_math)
    text = math_magic(text, "(", ")", lambda x: "(" + to_math(x) + ")")
    for m in re.finditer(r"\s+|[_^]?(\\[a-zA-Z0-9]+\s*|\\.|\w+|[{:c}-{:c}]|.)"
                         .format(MAGIC_FIRST, MAGIC_LAST),
                         text):
        v = m.group(0)
        fn = None
        if v.startswith("_"):
            fn = to_subscript
            v = v[1:]
        elif v.startswith("^"):
            fn = to_superscript
            v = v[1:]
        if v.startswith("\\"):
            mapped = math_map.get(v[1:].strip())
            if mapped is None:
                v = v[1:].strip()
            else:
                v = mapped
        elif v.isspace():
            v = ""
        if fn is not None:
            v = fn(v)
        if (((parts and parts[-1][-1].isalpha() and v and v[0].isalpha()) or
             (parts and parts[-1][-1].isdigit() and v and v[0].isdigit())) and
            len(parts[-1]) > 1 and len(v) > 1):
            v = " " + v
        if v:
            parts.append(v)

    text = "".join(parts)
    while True:
        orig = text
        text = re.sub(r"[{:c}-{:c}]".format(MAGIC_FIRST, MAGIC_LAST),
                      lambda m: magic_vec[ord(m.group(0)) - MAGIC_FIRST], text)
        if text == orig:
            break
    return text.strip()


def clean_value(config, title, no_strip=False):
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""

    def repl_1(m):
        return clean_value(config, m.group(1), no_strip=True)
    def repl_2(m):
        return clean_value(config, m.group(2), no_strip=True)
    def repl_link(m):
        if m.group(2) and m.group(2).lower() in ("file", "image"):
            return ""
        v = m.group(3).split("|")
        return clean_value(config, v[0], no_strip=True)
    def repl_link_bars(m):
        lnk = m.group(1)
        if re.match(r"(?si)(File|Image)\s*:", lnk):
            return ""
        return clean_value(config, m.group(4) or m.group(2) or "",
                           no_strip=True)

    def repl_1_sup(m):
        return to_superscript(clean_value(config, m.group(1)))

    def repl_1_sub(m):
        return to_subscript(clean_value(config, m.group(1)))

    def repl_1_checm(m):
        return to_chem(clean_value(config, m.group(1)))

    def repl_1_math(m):
        return to_math(m.group(1))

    assert isinstance(config, WiktionaryConfig)
    assert isinstance(title, str)
    title = re.sub(r"\{\{[^}]+\}\}", "", title)
    # Remove tables
    title = re.sub(r"(?s)\{\|.*?\|\}", "\n", title)
    # Remove references (<ref>...</ref>).
    title = re.sub(r"(?is)<\s*ref\s*[^>]*?>\s*.*?<\s*/\s*ref\s*>\n*", "", title)
    # Replace <br/> by comma space (it is used to express alternatives in some
    # declensions)
    title = re.sub(r"(?si)<\s*br\s*/?>\n*", ", ", title)
    # Change <div> and </div> to newlines.  Ditto for tr, li, table
    title = re.sub(r"(?si)<\s*/?\s*(div|tr|li|table)\b[^>]*>", "\n", title)
    # Change <td> </td> to spaces.  Ditto for th.
    title = re.sub(r"(?si)<\s*/?\s*(td|th)\b[^>]*>", " ", title)
    # Change <sup> ... </sup> to ^
    title = re.sub(r"(?si)<\s*sup\b[^>]*>\s*<\s*/\s*sup\s*>", "", title)
    title = re.sub(r"(?si)<\s*sup\b[^>]*>(.*?)<\s*/\s*sup\s*>",
                   repl_1_sup, title)
    # Change <sub> ... </sub> to _
    title = re.sub(r"(?si)<\s*sub\b[^>]*>\s*<\s*/\s*sup\s*>", "", title)
    title = re.sub(r"(?si)<\s*sub\b[^>]*>(.*?)<\s*/\s*sub\s*>",
                   repl_1_sub, title)
    # Change <chem> ... </chem> using subscripts for digits
    title = re.sub(r"(?si)<\s*chem\b[^>]*>(.*?)<\s*/\s*chem\s*>",
                   repl_1_checm, title)
    # Change <math> ... </math> using special formatting.
    title = re.sub(r"(?si)<\s*math\b[^>]*>(.*?)<\s*/\s*math\s*>",
                   repl_1_math, title)
    # Remove any remaining HTML tags.
    title = re.sub(r"(?s)<\s*[^/>][^>]*>", "", title)
    title = re.sub(r"(?s)<\s*/\s*[^>]+>", "", title)
    # Replace links by their text
    title = re.sub(r"(?si)\[\[\s*Category\s*:\s*([^]]+?)\s*\]\]", r"", title)
    title = re.sub(r"(?s)\[\[\s*([^]|]+?)\s*\|\s*([^]|]+?)"
                   r"(\s*\|\s*([^]|]+?))?\s*\]\]",
                   repl_link_bars, title)
    title = re.sub(r"(?s)\[\[\s*(([a-zA-z0-9]+)\s*:)?\s*([^][]+?)\]\]",
                   repl_link, title)
    title = re.sub(r"(?s)\[\[\s*:?([^]|]+?)\s*\]\]", repl_1, title)
    # Replace remaining HTML links by the URL.
    title = re.sub(r"\[(https?:)//[^]\s]+\s+([^]]+?)\s*\]", repl_2, title)
    # Remove any edit links to local pages
    title = re.sub(r"\[//[^]\s]+\s+edit\s*\]", "", title)
    # Remove italic and bold
    title = re.sub(r"''+", r"", title)
    # Replace HTML entities
    title = html.unescape(title)
    title = re.sub("\xa0", " ", title)  # nbsp
    # Replace whitespace sequences by a single space.
    title = re.sub(r"[ \t\r]+", " ", title)
    title = re.sub(r" *\n+", "\n", title)
    # This unicode quote seems to be used instead of apostrophe quite randomly
    # (about 4% of apostrophes in English entries, some in Finnish entries).
    # title = re.sub("\u2019", "'", title)  # Note: no r"..." here!
    # Replace strange unicode quotes with normal quotes
    # title = re.sub(r"”", '"', title)
    # Replace unicode long dash by normal dash
    # title = re.sub(r"–", "-", title)

    # Remove whitespace before periods and commas etc
    # XXX we might re-enable this, now trying without as it is removing some
    # instances where we would want to leave the space
    # title = re.sub(r" ([.,;:!?)])", repl_1, title)
    # Strip surrounding whitespace.
    if not no_strip:
        title = title.strip()
    # Normalize different ways of writing accents into the NFC canonical form
    title = unicodedata.normalize("NFC", title)
    return title
