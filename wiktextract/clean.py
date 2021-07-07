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

# Mapping from Latex names to Unicode characters/strings.  This is the
# default mapping (some cases are handled specially in the code).
math_map = {
    # XXX should probably change greek characters to non-slanted ones?
    "Angstroem": "Å",
    "Box": "□",
    "CapitalDifferentialD": "ⅅ",
    "ComplexI": "ⅈ",
    "ComplexJ": "ⅉ",
    "Delta": "𝛥",
    "DifferentialD": "ⅆ",
    "Downarrow": "⇓",
    "Euler": "Ɛ",
    "ExponentialE": "ⅇ",
    "Finv": "Ⅎ",
    "Gamma": "𝛤",
    "Im": "ℑ",
    "Lambda": "𝛬",
    "LeftArrowBar": "⇤",
    "Leftarrow": "⇐",
    "Leftarrow": "⇐",
    "Leftrightarrow": "⇔",
    "Lleftarrow": "⇚",
    "Longrightarrow": "⟹",
    "Lsh": "↰",
    "MapsDown": "↧",
    "MapsUp": "↥",
    "Micro": "μ",
    "Nearrow": "⇗",
    "Nwarrow": "⇖",
    "Omega": "𝛺",
    "Phi": "𝛷",
    "Pi": "𝛱",
    "Proportion": "∷",
    "Psi": "𝛹",
    "Re": "ℜ",
    "RightArrowBar": "⇥",
    "Rightarrow": "⇒",
    "Rightarrow": "⇒",
    "Rrightarrow": "⇛",
    "Rsh": "↱",
    "S": "§",
    "Searrow": "⇘",
    "Sigma": "𝛴",
    "Swarrow": "⇙",
    "Theta": "𝛩",
    "Uparrow": "⇑",
    "Updownarrow": "⇕",
    "Upsilon": "𝛶",
    "Vert": "‖",
    "Xi": "𝛯",
    "Yup": "⅄",
    "aleph": "א",
    "alpha": "𝛼",
    "angle": "∠",
    "approx": "≈",
    "arg": "arg",
    "ast": "∗",
    "backepsilon": "϶",
    "backprime": "‵",
    "backsim": "∽",
    "backslash": "\\",
    "because": "∵",
    "beta": "𝛽",
    "beth": "ב",
    "bigcap": "∩",
    "bigcup": "∪",
    "bigvee": "∨",
    "bigwedge": "∧",
    "blacksquare": "■",
    "bot": "⊥",
    "bullet": "•",
    "cap": "∩",
    "capwedge": "⩄",
    "cat": "⁀",
    "cdot": "·",
    "cdots": "⋯",
    "cent": "¢",
    "chi": "𝜒",
    "circ": "∘",
    "circlearrowleft": "↺",
    "circlearrowright": "↻",
    "circledR": "®",
    "colon": ":",
    "complement": "∁",
    "cong": "≅",
    "coprod": "∐",
    "cup": "∪",
    "curvearrowleft": "↶",
    "curvearrowright": "↷",
    "dagger": "†",
    "daleth": "ד",
    "dashleftarrow": "⇠",
    "dashrightarrow": "⇢",
    "ddagger": "‡",
    "delta": "𝛿",
    "diameter": "∅",
    "div": "÷",
    "dlsh": "↲",
    "dot\\bigvee": "⩒",
    "dot\\cap": "⩀",
    "dot\\cup": "⊍",
    "dot\\lor": "⩒",
    "dot\\vee": "⩒",
    "doteq": "≐",
    "dotplus": "∔",
    "dots": "…",
    "downarrow": "↓",
    "downdownarrows": "⇊",
    "downharpoonleft": "⇃",
    "downharpoonright": "⇂",
    "downuparrows": "⇵",
    "drsh": "↳",
    "ell": "ℓ",
    "emptyset": "∅",
    "epsilon": "𝜀",
    "eqcolon": "∹",
    "equiv": "≡",
    "eta": "𝜂",
    "eth": "ð",
    "exists": "∃",
    "ffun": "⇻",
    "footnotesize": "",
    "forall": "∀",
    "fourth": "′′′′",
    "gamma": "𝛾",
    "ge": ">",
    "geq": ">",
    "geq": "≥",
    "geqq": "≧",
    "geqslant": "⩾",
    "gg": "≫",
    "gimel": "ג",
    "gtrapprox": "⪆",
    "gtreqless": "⋛",
    "gtreqqless": "⪌",
    "gtrless": "≷",
    "gtrsim": "≳",
    "hookleftarrow": "↩",
    "hookrightarrow": "↪",
    "hslash": "ℏ",
    "iff": "⟺",
    "iint": "∫∫",
    "iint": "∫∫∫",
    "imath": "ı",
    "implies": "⟹",
    "in": "∈",
    "infty": "∞",
    "int": "∫",
    "intercal": "⊺",
    "invamp": "⅋",
    "iota": "𝜄",
    "jmath": "ȷ",
    "kappa": "𝜅",
    "lambda": "𝜆",
    "land": "∧",
    "langle": "⟨",
    "large": "",
    "lbrace": "{",
    "lbrack": "[",
    "lceil": "⌈",
    "ldots": "...",
    "ldots": "…",
    "le": "<",
    "leftarrow": "←",
    "leftarrowtail": "↢",
    "leftarrowtriangle": "⇽",
    "leftharpoondown": "↽",
    "leftharpoonup": "↼",
    "leftleftarrows": "⇇",
    "leftrightarrow": "↔",
    "leftrightarrows": "⇆",
    "leftrightarrowtriangle": "⇿",
    "leftrightharpoons": "⇋",
    "leftrightsquigarrow": "↭",
    "leftsquigarrow": "⇜",
    "leq": "<",
    "leq": "≤",
    "leqq": "≦",
    "leqslant": "⩽",
    "lessapprox": "⪅",
    "lesseqgtr": "⋚",
    "lesseqqgtr": "⪋",
    "lessgtr": "≶",
    "lessim": "≲",
    "lfloor": "⌊",
    "lightning": "↯",
    "ll": "≪",
    "lnot": "¬",
    "looparrowleft": "↫",
    "looparrowright": "↬",
    "lor": "∨",
    "mapsfrom": "↤",
    "mapsto": "↦",
    "measuredangle": "∡",
    "mho": "℧",
    "mid": "∣",
    "mlcp": "⫛",
    "mod": " mod ",
    "models": "⊨",
    "mp": "∓",
    "mu": "𝜇",
    "nLeftarrow": "⇍",
    "nLeftrightarrow": "⇎",
    "nRightarrow": "⇏",
    "nabla": "∇",
    "nearrow": "↗",
    "neg": "¬",
    "neq": "≠",
    "nexists": "∄",
    "ni": "∋",
    "nleftarrow": "↚",
    "nleftrightarrow": "↮",
    "nmid": "∤",
    "nni": "∌",
    "normalsize": "",
    "not\\in": "∉",
    "not\\ni": "∌",
    "not\\preceq": "⋠",
    "not\\trianglelefteq": "⋬",
    "not\\trianglerighteq": "⋭",
    "not\\subset": "⊄",
    "not\\subseteq": "⊈",
    "not\\succeq": "⋡",
    "not\\supset": "⊅",
    "not\\supseteq": "⊉",
    "not\\vartriangleleft": "⋪",
    "not\\vartriangleright": "⋫",
    "notin": "∉",
    "nparallel": "∦",
    "nrightarrow": "↛",
    "nu": "𝜈",
    "nwarrow": "↖",
    "oiint": "∮∮",
    "oint": "∮",
    "omega": "𝜔",
    "oplus": "⊕",
    "oslash": "⊘",
    "otimes": "⊗",
    "over": "/",
    "overset?=": "≟",
    "overset{?}{=}": "≟",
    "overset{\\operatorname{def}}{=}": "≝",
    "parallel": "∥",
    "partial": "∂",
    "perp": "⊥",
    "pfun": "⇸",
    "phi": "𝜙",
    "pi": "𝜋",
    "pm": "±",
    "pounds": "£",
    "prec": "≺",
    "preceq": "⪯",
    "prime": "′",
    "prod": "∏",
    "propto": "∝",
    "psi": "𝜓",
    "rangle": "⟩",
    "rarr": "→",
    "rbrace": "}",
    "rbrack": "]",
    "rceil": "⌉",
    "rfloor": "⌋",
    "rho": "𝜌",
    "rightangle": "∟",
    "rightarrow": "→",
    "rightarrowtail": "↣",
    "rightarrowtriangle": "⇾",
    "rightharpoondown": "⇁",
    "rightharpoonup": "⇀",
    "rightleftarrows": "⇄",
    "rightleftharpoons": "⇌",
    "rightrightarrows": "⇉",
    "rightsquigarrow": "⇝",
    "rtimes": "⋊",
    "scriptsize": "",
    "searrow": "↘",
    "second": "′′",
    "sigma": "𝜎",
    "sim": "∼",
    "simeq": "≃",
    "slash": "∕",
    "small": "",
    "smallsetminus": "∖",
    "square": "□",
    "spddot": "̈",
    "sphat": "^",
    "sphericalangle": "∢",
    "sptilde": "~",
    "sqcap": "⊓",
    "sqcup": "⊔",
    "sqrt": "√",  # ∛ ∜ - partly special handling below
    "subset": "⊂",
    "subseteq": "⊆",
    "subsetneq": "⊊",
    "succ": "≻",
    "succeq": "⪰",
    "sum": "∑",
    "supset": "⊃",
    "supseteq": "⊇",
    "supsetneq": "⊋",
    "swarrow": "↙",
    "tau": "𝜏",
    "tcohm": "Ω",
    "textbackslash": "\\",
    "textbar": "|",
    "textbullet": "•",
    "textgreater": ">",
    "textless": "<",
    "textprime": "′",
    "therefore": "∴",
    "theta": "𝜃",
    "third": "′′′",
    "times": "⨯",
    "tiny": "",
    "to": "→",
    "top": "⊤",
    "triangle": "∆",
    "trianglelefteq": "⊴",
    "triangleq": "≜",
    "trianglerighteq": "⊵",
    "twoheadleftarrow": "↞",
    "twoheadrightarrow": "↠",
    "uparrow": "↑",
    "updownarrow": "↕",
    "updownarrows": "⇅",
    "upharpoonleft": "↿",
    "upharpoonright": "↾",
    "uplus": "⊎",
    "upsilon": "𝜐",
    "upuparrows": "⇈",
    "varbeta": "β",
    "varepsilon": "ε",
    "varkappa": "𝜘",
    "varnothing": "∅",
    "varphi": "𝜑",
    "varpi": "𝜛",
    "varrho": "𝜚",
    "varsigma": "ς",
    "vartheta": "θ",
    "vartriangleleft": "⊲",
    "vartriangleright": "⊳",
    "vdash": "⊢",
    "vdots": "⋮",
    "vee": "∨",
    "veebar": "⊻",
    "vert": "|",
    "wedge": "∧",
    "widehat=": "≙",
    "widehat{=}": "≙",
    "wp": "℘",
    "wr": "≀",
    "xi": "𝜉",
    "yen": "¥",
    "zeta": "𝜁",

    # Accents XXX these really should be handled specially with diacritics
    # after argument
    "acute": "́",
    "bar": "̄",
    "breve": "̆",
    "check": "̌",
    "dddot": "⃛",
    "dddot": "⃜",
    "ddot": "̈",
    "dot": "̇",
    "grave": "̀",
    "hat": "̂",
    "lvec": "⃐",
    "mathring": "̊",
    "not": "̸",
    "overline": "◌̅",
    "tilde": "̃",
    "vec": "⃑",


    # Some ignored operators
    "bigl": "",
    "bigr": "",
    "left": "",
    "right": "",
    "style": "",
    "textstyle": "",
    "mathrm": "",
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
    "0": "𝟘",
    "1": "𝟙",
    "2": "𝟚",
    "3": "𝟛",
    "4": "𝟜",
    "5": "𝟝",
    "6": "𝟞",
    "7": "𝟟",
    "8": "𝟠",
    "9": "𝟡",
}

def mathcal_fn(text):
    return "".join(mathcal_map.get(x, x) for x in text)

def mathfrak_fn(text):
    return "".join(mathfrak_map.get(x, x) for x in text)

def mathbb_fn(text):
    return "".join(mathbb_map.get(x, x) for x in text)

def to_math(text):
    """Converts a mathematical formula to ASCII."""
    # print("to_math: {!r}".format(text))
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
            elif re.match(r"\\pmod\b", v):
                v = v[5:].strip()
                v = "(mod " + expand_group(v) + ")"
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
            elif re.match(r"\\(frac|binom)($|[0-9]|\b)", v):
                m = re.match(r"\\(frac|binom)\s*(\\[a-zA-Z]+|\\.|.)\s*"
                             r"(\\[a-zA-Z]+|\\.|.)$", v)
                if not m:
                    print("MATH FRAC/BINOM ERROR: {!r}".format(v))
                    return v
                op, a, b = m.groups()
                a = expand_group(a.strip())
                b = expand_group(b.strip())
                if len(a) > 1:
                    a = "(" + a + ")"
                if len(b) > 1:
                    b = "(" + b + ")"
                if op == "frac":
                    v = a + "/" + b
                elif op == "binom":
                    v = "binom({}, {})".format(a, b)
                else:
                    # Should never get here
                    v = "{}({})".format(op, v)
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
        for m in re.finditer(r"\s+|"
                             r"\\frac\s*(\\[a-zA-Z]+|\\.|.)\s*"
                             r"(\\dot\\(bigvee|cup|cap|lor|vee)|"
                             r"\\not\\(subset|supset|subseteq|supseteq|in|ni|"
                             r"preceq|succeq|vartrianglelefteq|"
                             r"vartrianglerighteq|trianglelefteq|"
                             r"trianglerighteq)|"
                             r"\\widehat\{=\}|\\widehat=|"
                             r"\\overset\{?\}\{=\}|"
                             r"\\overset\?=|"
                             r"\\overset\{\\operatorname\{def\}\}\{=\}|"
                             r"\\[a-zA-Z]+|\\.|.)|"
                             r"(\\(mathcal|mathfrak|mathbb|text|begin|end|pmod)"
                             r"\b\s*|"
                             r"\\sqrt\b(\[\d+\])?)?"
                             r"[_^]?(\\[a-zA-Z]+\s*|\\.|\w+|.)", text):
            v = expand_group(m.group(0))
            if v:
                parts.append(v)

        text = "".join(parts)
        return text

    text = recurse(text)
    # print("math text final: {!r}".format(text))
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

    # Remove any remaining templates
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
    while True:
        # Links may be nested, so keep replacing until there is no more change.
        orig = title
        title = re.sub(r"(?si)\[\[\s*Category\s*:\s*([^]]+?)\s*\]\]",
                       r"", title)
        title = re.sub(r"(?s)\[\[\s*:?([^]|#]+?)\s*(#[^][|]*?)?\]\]",
                       repl_1, title)
        title = re.sub(r"(?s)\[\[\s*(([a-zA-z0-9]+)\s*:)?\s*([^][#|]+?)"
                       r"\s*(#[^][|]*?)?\|?\]\]",
                       repl_link, title)
        title = re.sub(r"(?s)\[\[\s*([^][|]+?)\s*\|"
                       r"\s*([^][|]+?)(\s*\|\s*([^]|]+?))?\s*\]\]",
                       repl_link_bars, title)
        if title == orig:
            break
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
