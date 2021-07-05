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
    "∞": " ᪲"
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
    "backsim": "∽",
    "tiny": "",
    "scriptsize": "",
    "footnotesize": "",
    "small": "",
    "normalsize": "",
    "large": "",
    "ge": ">",
    "geq": ">",
    "le": "<",
    "leq": "<",
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
    "textprime": "′",
    "second": "′′",
    "third": "′′′",
    "fourth": "′′′′",
    "backprime": "‵",
    "dagger": "†",
    "ddagger": "‡",
    "bullet": "•",
    "ldots": "...",
    "dots": "…",
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
    "leftrightarrow": "↔",
    "uparrow": "↑",
    "downarrow": "↓",
    "updownarrow": "↕",
    "nwarrow": "↖",
    "nearrow": "↗",
    "searrow": "↘",
    "swarrow": "↙",
    "nleftarrow": "↚",
    "nrightarrow": "↛",
    "twoheadleftarrow": "↞",
    "twoheadrightarrow": "↠",
    "leftarrowtail": "↢",
    "rightarrowtail": "↣",
    "mapsfrom": "↤",
    "MapsUp": "↥",
    "mapsto": "↦",
    "MapsDown": "↧",
    "hookleftarrow": "↩",
    "hookrightarrow": "↪",
    "looparrowleft": "↫",
    "looparrowright": "↬",
    "leftrightsquigarrow": "↭",
    "nleftrightarrow": "↮",
    "lightning": "↯",
    "Lsh": "↰",
    "Rsh": "↱",
    "dlsh": "↲",
    "drsh": "↳",
    "curvearrowleft": "↶",
    "curvearrowright": "↷",
    "circlearrowleft": "↺",
    "circlearrowright": "↻",
    "leftharpoonup": "↼",
    "leftharpoondown": "↽",
    "upharpoonright": "↾",
    "upharpoonleft": "↿",
    "rightharpoonup": "⇀",
    "rightharpoondown": "⇁",
    "downharpoonright": "⇂",
    "downharpoonleft": "⇃",
    "rightleftarrows": "⇄",
    "updownarrows": "⇅",
    "leftrightarrows": "⇆",
    "leftleftarrows": "⇇",
    "upuparrows": "⇈",
    "rightrightarrows": "⇉",
    "downdownarrows": "⇊",
    "leftrightharpoons": "⇋",
    "rightleftharpoons": "⇌",
    "nLeftarrow": "⇍",
    "nLeftrightarrow": "⇎",
    "nRightarrow": "⇏",
    "Leftarrow": "⇐",
    "Uparrow": "⇑",
    "Rightarrow": "⇒",
    "Downarrow": "⇓",
    "Leftrightarrow": "⇔",
    "Updownarrow": "⇕",
    "Nwarrow": "⇖",
    "Nearrow": "⇗",
    "Searrow": "⇘",
    "Swarrow": "⇙",
    "Lleftarrow": "⇚",
    "Rrightarrow": "⇛",
    "leftsquigarrow": "⇜",
    "rightsquigarrow": "⇝",
    "dashleftarrow": "⇠",
    "dashrightarrow": "⇢",
    "LeftArrowBar": "⇤",
    "RightArrowBar": "⇥",
    "downuparrows": "⇵",
    "pfun": "⇸",
    "ffun": "⇻",
    "leftarrowtriangle": "⇽",
    "rightarrowtriangle": "⇾",
    "leftrightarrowtriangle": "⇿",
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
    "backslash": "\\",
    "spddot": "̈",
    "sphat": "^",
    "Micro": "μ",
    "eth": "ð",
    "imath": "ı",
    "jmath": "ȷ",
    "circledR": "®",
    "therefore": "∴",
    "because": "∵",
    "Proportion": "∷",
    "eqcolon": "∹",

    "alpha": "𝛼",
    "beta": "𝛽",
    "varbeta": "β",
    "gamma": "𝛾",
    "delta": "𝛿",
    "epsilon": "𝜀",
    "varepsilon": "ε",
    "backepsilon": "϶",
    "zeta": "𝜁",
    "eta": "𝜂",
    "theta": "𝜃",
    "vartheta": "θ",
    "iota": "𝜄",
    "kappa": "𝜅",
    "varkappa": "𝜘",
    "lambda": "𝜆",
    "mu": "𝜇",
    "nu": "𝜈",
    "xi": "𝜉",
    "pi": "𝜋",
    "varpi": "𝜛",
    "rho": "𝜌",
    "varrho": "𝜚",
    "sigma": "𝜎",
    "varsigma": "ς",
    "tau": "𝜏",
    "upsilon": "𝜐",
    "phi": "𝜙",
    "varphi": "𝜑",
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
    "hslash": "ℏ",
    "invamp": "⅋",

    "grave": "̀",
    "acute": "́",
    "hat": "̂",
    "tilde": "̃",
    "bar": "̄",
    "breve": "̆",
    "dot": "̇",
    "ddot": "̈",
    "dddot": "⃛",
    "dddot": "⃜",
    "mathring": "̊",
    "check": "̌",
    "not": "̸",

    "textstyle": "",
    "sqrt": "√",  # ∛ ∜
    "frac": " / ",
    "sum": "∑",
    "prod": "∏",
    "coprod": "∐",
    "lvec": "⃐",
    "vec": "⃑",
    "left": "",
    "right": "",
    "bigl": "",
    "bigr": "",
    "lbrace": "{",
    "rbrace": "}",
    "lbrack": "[",
    "rbrack": "]",
    "langle": "⟨",
    "rangle": "⟩",
    "vert": "|",
    "Vert": "‖",
    "CapitalDifferentialD": "ⅅ",
    "DifferentialD": "ⅆ",
    "ExponentialE": "ⅇ",
    "ComplexI": "ⅈ",
    "ComplexJ": "ⅉ",
    "over": "/",

    "style": "",
}

mathcal_map = {
    "A": "𝒜",
    "B": "ℬ",
    "C": "𝒞",
    "D": "𝒟",
    "E": "ℰ",
    "F": "ℱ",
    "G": "𝒢",
    "H": "ℋ",
    "I": "ℐ",
    "J": "𝒥",
    "K": "𝒦",
    "L": "ℒ",
    "M": "ℳ",
    "N": "𝒩",
    "O": "𝒪",
    "P": "𝒫",
    "Q": "𝒬",
    "R": "ℛ",
    "S": "𝒮",
    "T": "𝒯",
    "U": "𝒰",
    "V": "𝒱",
    "W": "𝒲",
    "X": "𝒳",
    "Y": "𝒴",
    "Z": "𝒵",
    "a": "𝒶",
    "b": "𝒷",
    "c": "𝒸",
    "d": "𝒹",
    "e": "ℯ",
    "f": "𝒻",
    "g": "ℊ",
    "h": "𝒽",
    "i": "𝒾",
    "j": "𝒿",
    "k": "𝓀",
    "l": "𝓁",
    "m": "𝓂",
    "n": "𝓃",
    "o": "ℴ",
    "p": "𝓅",
    "q": "𝓆",
    "r": "𝓇",
    "s": "𝓈",
    "t": "𝓉",
    "u": "𝓊",
    "v": "𝓋",
    "w": "𝓌",
    "x": "𝓍",
    "y": "𝓎",
    "z": "𝓏",
}

mathfrak_map = {
    "A": "𝔄",
    "B": "𝔅",
    "C": "ℭ",
    "D": "𝔇",
    "E": "𝔈",
    "F": "𝔉",
    "G": "𝔊",
    "H": "ℌ",
    "J": "𝔍",
    "K": "𝔎",
    "L": "𝔏",
    "M": "𝔐",
    "N": "𝔑",
    "O": "𝔒",
    "P": "𝔓",
    "Q": "𝔔",
    "S": "𝔖",
    "T": "𝔗",
    "U": "𝔘",
    "V": "𝔙",
    "W": "𝔚",
    "X": "𝔛",
    "Y": "𝔜",
    "Z": "ℨ",
}

mathbb_map = {
    "A": "𝔸",
    "B": "𝔹",
    "C": "ℂ",
    "D": "𝔻",
    "E": "𝔼",
    "F": "𝔽",
    "G": "𝔾",
    "H": "ℍ",
    "I": "𝕀",
    "J": "𝕁",
    "K": "𝕂",
    "L": "𝕃",
    "M": "𝕄",
    "N": "ℕ",
    "O": "𝕆",
    "P": "ℙ",
    "Q": "ℚ",
    "R": "ℝ",
    "S": "𝕊",
    "T": "𝕋",
    "U": "𝕌",
    "V": "𝕍",
    "W": "𝕎",
    "X": "𝕏",
    "Y": "𝕐",
    "Z": "ℤ",
    "a": "𝕒",
    "b": "𝕓",
    "c": "𝕔",
    "d": "𝕕",
    "e": "𝕖",
    "f": "𝕗",
    "g": "𝕘",
    "h": "𝕙",
    "i": "𝕚",
    "j": "𝕛",
    "k": "𝕜",
    "l": "𝕝",
    "m": "𝕞",
    "n": "𝕟",
    "o": "𝕠",
    "p": "𝕡",
    "q": "𝕢",
    "r": "𝕣",
    "s": "𝕤",
    "t": "𝕥",
    "u": "𝕦",
    "v": "𝕧",
    "w": "𝕨",
    "x": "𝕩",
    "y": "𝕪",
    "z": "𝕫",
    "pi": "ℼ",
    "gamma": "ℽ",
    "Gamma": "ℾ",
    "Pi": "ℿ",
    "Sigma": "⅀",
}

def mathcal_fn(text):
    return "".join(mathcal_map.get(x, x) for x in text)

def mathfrak_fn(text):
    return "".join(mathfrak_map.get(x, x) for x in text)

def mathbb_fn(text):
    return "".join(mathbb_map.get(x, x) for x in text)

def to_math(text):
    """Converts a mathematical formula to ASCII."""
    print("to_math: {!r}".format(text))
    magic_vec = []

    def expand(text):
        while True:
            orig = text
            text = re.sub(r"[{:c}-{:c}]".format(MAGIC_FIRST, MAGIC_LAST),
                          lambda m: magic_vec[ord(m.group(0)) - MAGIC_FIRST],
                          text)
            if text == orig:
                break
        return text.strip()

    def recurse(text):
        def math_magic(text, left, right, fn):
            regexp = r"{}([^{}{}]+){}".format(
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

        def expand_group(v):
            fn = None
            if re.match(r"\\mathcal\b", v):
                fn = mathcal_fn
                v = v[8:].strip()
            elif re.match(r"\\mathfrak\b", v):
                fn = mathfrak_fn
                v = v[9:].strip()
            elif re.match(r"\\mathbb\b", v):
                fn = mathbb_fn
                v = v[7:]
            elif re.match(r"\\(begin|end)\b", v):
                v = ""  # Skip
            elif re.match(r"\\text\b", v):
                v = v[5:]
            elif re.match(r"\\sqrt\[", v):
                a = v[6:-1].strip()
                if a == "2":
                    v = "√"
                elif a == "3":
                    v = "∛",
                elif a == "4":
                    v = "∜"
                else:
                    v = to_superscript(a) + "√"
            elif re.match(r"\\sqrt($|[0-9]|\b)", v):
                v = "√"
            elif re.match(r"\\frac($|[0-9]|\b)", v):
                print("frac: {!r}".format(v))
                m = re.match(r"\\frac\s*(\\[a-zA-Z]+|\\.|.)\s*"
                             r"(\\[a-zA-Z]+|\\.|.)$", v)
                if not m:
                    print("MATH FRAC ERROR")
                    return v
                a, b = m.groups()
                a = expand_group(a.strip())
                b = expand_group(b.strip())
                if len(a) > 1:
                    a = "(" + a + ")"
                if len(b) > 1:
                    b = "(" + b + ")"
                v = a + "/" + b
            elif v.startswith("_"):
                fn = to_subscript
                v = v[1:]
            elif v.startswith("^"):
                fn = to_superscript
                v = v[1:]
            if v.startswith("\\"):
                mapped = math_map.get(v[1:].strip())
                if mapped is None:
                    if v[1:].strip().isalnum():
                        v = " " + v[1:].strip() + " "
                    else:
                        v = v[1:].strip()
                else:
                    v = mapped
            elif v.isspace() or v in ("&",):  # Ignore certain special chars
                v = ""
            if fn is not None:
                v = expand(v)
                v = fn(v)
            if (((parts and parts[-1][-1].isalpha() and v and v[0].isalpha()) or
                 (parts and parts[-1][-1].isdigit() and v and
                  v[0].isdigit())) and
                len(parts[-1]) > 1 and len(v) > 1):
                v = " " + v
            v = expand(v)
            return v

        parts = []
        while True:
            orig = text
            text = math_magic(text, "{", "}", recurse)
            # text = math_magic(text, "(", ")", lambda x: "(" + recurse(x) + ")")
            if text == orig:
                break
        print("BEFORE ITER: {!r}".format(text))
        for m in re.finditer(r"\s+|"
                             r"\\frac\s*(\\[a-zA-Z]+|\\.|.)\s*"
                             r"(\\[a-zA-Z]+|\\.|.)|"
                             r"(\\(mathcal|mathfrak|mathbb|text|begin|end)"
                             r"\b\s*|"
                             r"\\sqrt\b(\[\d+\])?)?"
                             r"[_^]?(\\[a-zA-Z]+\s*|\\.|\w+|.)", text):
            v = expand_group(m.group(0))
            if v:
                parts.append(v)

        text = "".join(parts)
        return text

    text = recurse(text)
    print("math text final: {!r}".format(text))
    return text


def clean_value(config, title, no_strip=False):
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(title, str)

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

    def repl_1_chem(m):
        return to_chem(clean_value(config, m.group(1)))

    def repl_1_math(m):
        return to_math(m.group(1))

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
                   repl_1_chem, title)
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
