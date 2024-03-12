# This file contains code to clean Wiktionary annotations from a string and to
# produce plain text from it, typically for glossary entries but this is also
# called for various other data to produce clean strings.
#
# This file also contains code for cleaning qualifiers for the "tags" field.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import html
import unicodedata
from typing import Callable, Optional, Union
from wikitextprocessor.common import MAGIC_FIRST, MAGIC_LAST
from wikitextprocessor.core import (
    NamespaceDataEntry,
    TemplateArgs,
)
from wikitextprocessor.common import URL_STARTS
from .wxr_context import WiktextractContext

######################################################################
# Cleaning values into plain text.
######################################################################

superscript_ht: dict[str, str] = {
    "0": "⁰",
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
    "−": "⁻",
    "‐": "⁻",
    "–": "⁻",
    "—": "⁻",
    "一": "⁻",
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
    "∞": "\u2002᪲",  # This is a KLUDGE
}

subscript_ht: dict[str, str] = {
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
    "−": "₋",
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


def to_superscript(text: str) -> str:
    "Converts text to superscript."
    if not text:
        return ""
    if all(x in superscript_ht for x in text):
        return "".join(superscript_ht[x] for x in text)
    if len(text) == 1:
        return "^" + text
    return "^({})".format(text)


def to_subscript(text: str) -> str:
    """Converts text to subscript."""
    if not text:
        return ""
    if all(x in subscript_ht for x in text):
        return "".join(subscript_ht[x] for x in text)
    if len(text) == 1:
        return "_" + text
    return "_({})".format(text)


def to_chem(text: str) -> str:
    """Converts text to chemical formula, making digits subscript."""
    return "".join(to_subscript(x) if x.isdigit() else x for x in text)


# Mapping from Latex names to Unicode characters/strings.  This is the
# default mapping (some cases are handled specially in the code).
math_map: dict[str, str] = {
    # XXX should probably change greek characters to non-slanted ones?
    "AC": "∿",
    "APLcomment": "⍝",
    "APLdownarrowbox": "⍗",
    "APLinput": "⍞",
    "APLinv": "⌹",
    "APLleftarrowbox": "⍇",
    "APLlog": "⍟",
    "APLrightarrowbox": "⍈",
    "APLuparrowbox": "⍐",
    "Angstroem": "Å",
    "Bot": "⫫",
    "Box": "□",
    "Bumpeq": "≎",
    "CIRCLE": "●",
    "Cap": "⋒",
    "CapitalDifferentialD": "ⅅ",
    "CheckedBox": "☑",
    "Circle": "○",
    "Coloneqq": "⩴",
    "ComplexI": "ⅈ",
    "ComplexJ": "ⅉ",
    "Cup": "⋓",
    "Delta": "Δ",
    "Diamond": "◇",
    "Diamondblack": "◆",
    "Diamonddot": "⟐",
    "DifferentialD": "ⅆ",
    "Digamma": "Ϝ",
    "Doteq": "≑",
    "DownArrowBar": "⤓",
    "DownLeftTeeVector": "⥞",
    "DownLeftVectorBar": "⥖",
    "DownRightTeeVector": "⥟",
    "DownRightVectorBar": "⥗",
    "Downarrow": "⇓",
    "Equal": "⩵",
    "Euler": "Ɛ",
    "ExponentialE": "ⅇ",
    "ExponetialE": "ⅇ",
    "Finv": "Ⅎ",
    "Gamma": "Γ",
    "Im": "ℑ",
    "Join": "⨝",
    "Koppa": "Ϟ",
    "LEFTCIRCLE": "◖",
    "LEFTcircle": "◐",
    "LHD": "◀",
    "LVec": "x⃖",
    "Lambda": "Λ",
    "Lbag": "⟅",
    "LeftArrowBar": "⇤",
    "LeftDownTeeVector": "⥡",
    "LeftDownVectorBar": "⥙",
    "LeftTeeVector": "⥚",
    "LeftTriangleBar": "⧏",
    "LeftUpTeeVector": "⥠",
    "LeftUpVectorBar": "⥘",
    "LeftVectorBar": "⥒",
    "Leftarrow": "⇐",
    "Leftrightarrow": "⇔",
    "Lleftarrow": "⇚",
    "Longleftarrow": "⟸",
    "Longleftrightarrow": "⟺",
    "Longmapsfrom": "⟽",
    "Longmapsto": "⟾",
    "Longrightarrow": "⟹",
    "Lparen": "⦅",
    "Lsh": "↰",
    "MapsDown": "↧",
    "MapsUp": "↥",
    "Mapsfrom": "⤆",
    "Mapsto": "⤇",
    "Micro": "µ",
    "Nearrow": "⇗",
    "NestedGreaterGreater": "⪢",
    "NestedLessLess": "⪡",
    "NotGreaterLess": "≹",
    "NotGreaterTilde": "≵",
    "NotLessTilde": "≴",
    "Nwarrow": "⇖",
    "Omega": "Ω",
    "Phi": "Φ",
    "Pi": "Π",
    "Proportion": "∷",
    "Psi": "Ψ",
    "Qoppa": "Ϙ",
    "RHD": "▶",
    "RIGHTCIRCLE": "◗",
    "RIGHTcircle": "◑",
    "Rbag": "⟆",
    "Re": "ℜ",
    "RightArrowBar": "⇥",
    "RightDownTeeVector": "⥝",
    "RightDownVectorBar": "⥕",
    "RightTeeVector": "⥛",
    "RightTriangleBar": "⧐",
    "RightUpTeeVector": "⥜",
    "RightUpVectorBar": "⥔",
    "RightVectorBar": "⥓",
    "Rightarrow": "⇒",
    "Rparen": "⦆",
    "Rrightarrow": "⇛",
    "Rsh": "↱",
    "S": "§",
    "Same": "⩶",
    "Sampi": "Ϡ",
    "Searrow": "⇘",
    "Sigma": "Σ",
    "Square": "☐",
    "Stigma": "Ϛ",
    "Subset": "⋐",
    "Sun": "☉",
    "Supset": "⋑",
    "Swarrow": "⇙",
    "Theta": "Θ",
    "Top": "⫪",
    "UpArrowBar": "⤒",
    "Uparrow": "⇑",
    "Updownarrow": "⇕",
    "Upsilon": "Υ",
    "VDash": "⊫",
    "VERT": "⦀",
    "Vdash": "⊩",
    "Vert": "‖",
    "Vvdash": "⊪",
    "XBox": "☒",
    "Xi": "Ξ",
    "Yup": "⅄",
    "_": "_",
    "aleph": "א",
    "alpha": "α",
    "amalg": "⨿",
    "anchor": "⚓",
    "angle": "∠",
    "approx": "≈",
    "approxeq": "≊",
    "aquarius": "♒",
    "arg": "arg",
    "aries": "♈",
    "arrowbullet": "➢",
    "ast": "∗",
    "asymp": "≍",
    "backepsilon": "϶",
    "backprime": "‵",
    "backsim": "∽",
    "backsimeq": "⋍",
    "backslash": "",
    "ballotx": "✗",
    "barin": "⋶",
    "barleftharpoon": "⥫",
    "barrightharpoon": "⥭",
    "barwedge": "⊼",
    "because": "∵",
    "beta": "β",
    "beth": "ב",
    "between": "≬",
    "bigcap": "∩",
    "bigcup": "∪",
    "biginterleave": "⫼",
    "bigodot": "⨀",
    "bigoplus": "⨁",
    "bigotimes": "⨂",
    "bigsqcap": "⨅",
    "bigsqcup": "⨆",
    "bigstar": "★",
    "bigtriangledown": "▽",
    "bigtriangleup": "△",
    "biguplus": "⨄",
    "bigvee": "∨",
    "bigwedge": "∧",
    "bij": "⤖",
    "biohazard": "☣",
    "blacklozenge": "⧫",
    "blacksmiley": "☻",
    "blacksquare": "■",
    "blacktriangledown": "▾",
    "blacktriangleleft": "◂",
    "blacktriangleright": "▸",
    "blacktriangleup": "▴",
    "bot": "⊥",
    "bowtie": "⋈",
    "boxast": "⧆",
    "boxbar": "◫",
    "boxbox": "⧈",
    "boxbslash": "⧅",
    "boxcircle": "⧇",
    "boxdot": "⊡",
    "boxminus": "⊟",
    "boxplus": "⊞",
    "boxslash": "⧄",
    "boxtimes": "⊠",
    "bullet": "•",
    "bumpeq": "≏",
    "cancer": "♋",
    "cap": "∩",
    "capricornus": "♑",
    "capwedge": "⩄",
    "cat": "⁀",
    "cdot": "·",
    "cdots": "⋯",
    "cent": "¢",
    "checkmark": "✓",
    "chi": "χ",
    "circ": "∘",
    "circeq": "≗",
    "circlearrowleft": "↺",
    "circlearrowright": "↻",
    "circledR": "®",
    "circledast": "⊛",
    "circledbslash": "⦸",
    "circledcirc": "⊚",
    "circleddash": "⊝",
    "circledgtr": "⧁",
    "circledless": "⧀",
    "clubsuit": "♣",
    "colon": ":",
    "coloneq": "≔",
    "complement": "∁",
    "cong": "≅",
    "coprod": "∐",
    "corresponds": "≙",
    "cup": "∪",
    "curlyeqprec": "⋞",
    "curlyeqsucc": "⋟",
    "curlyvee": "⋎",
    "curlywedge": "⋏",
    "curvearrowleft": "↶",
    "curvearrowright": "↷",
    "dagger": "†",
    "daleth": "ד",
    "dashleftarrow": "⇠",
    "dashrightarrow": "⇢",
    "dashv": "⊣",
    "ddagger": "‡",
    "delta": "δ",
    "diameter": "∅",
    "diamond": "⋄",
    "diamondsuit": "♢",
    "digamma": "ϝ",
    "div": "÷",
    "divideontimes": "⋇",
    "dlsh": "↲",
    "dot\\bigvee": "⩒",
    "dot\\cap": "⩀",
    "dot\\cup": "⊍",
    "dot\\lor": "⩒",
    "dot\\vee": "⩒",
    "doteq": "≐",
    "dotplus": "∔",
    "dots": "…",
    "doublebarwedge": "⩞",
    "downarrow": "↓",
    "downdownarrows": "⇊",
    "downdownharpoons": "⥥",
    "downharpoonleft": "⇃",
    "downharpoonright": "⇂",
    "downuparrows": "⇵",
    "downupharpoons": "⥯",
    "drsh": "↳",
    "dsub": "⩤",
    "earth": "♁",
    "eighthnote": "♪",
    "ell": "ℓ",
    "emptyset": "∅",
    "epsilon": "ϵ",
    "eqcirc": "≖",
    "eqcolon": "∹",
    "eqsim": "≂",
    "eqslantgtr": "⪖",
    "eqslantless": "⪕",
    "equiv": "≡",
    "eta": "η",
    "eth": "ð",
    "exists": "∃",
    "fallingdotseq": "≒",
    "fcmp": "⨾",
    "female": "♀",
    "ffun": "⇻",
    "finj": "⤕",
    "fint": "⨏",
    "flat": "♭",
    "footnotesize": "",
    "forall": "∀",
    "fourth": "⁗",
    "frown": "⌢",
    "frownie": "☹",
    "gamma": "γ",
    "ge": ">",
    "gemini": "♊",
    "geq": "≥",
    "geqq": "≧",
    "geqslant": "⩾",
    "gg": "≫",
    "ggcurly": "⪼",
    "ggg": "⋙",
    "gimel": "ג",
    "gnapprox": "⪊",
    "gneq": "⪈",
    "gneqq": "≩",
    "gnsim": "⋧",
    "gtrapprox": "⪆",
    "gtrdot": "⋗",
    "gtreqless": "⋛",
    "gtreqqless": "⪌",
    "gtrless": "≷",
    "gtrsim": "≳",
    "hash": "⋕",
    "heartsuit": "♡",
    "hookleftarrow": "↩",
    "hookrightarrow": "↪",
    "hslash": "ℏ",
    "iddots": "⋰",
    "iff": "⟺",
    "iiiint": "⨌",
    "iiint": "∭",
    "iint": "∬",
    "imath": "ı",
    "implies": "⟹",
    "in": "∈",
    "infty": "∞",
    "int": "∫",
    "intercal": "⊺",
    "interleave": "⫴",
    "invamp": "⅋",
    "invdiameter": "⍉",
    "invneg": "⌐",
    "iota": "ι",
    "jmath": "ȷ",
    "jupiter": "♃",
    "kappa": "κ",
    "koppa": "ϟ",
    "lambda": "λ",
    "land": "∧",
    "lang": "⟪",
    "langle": "⟨",
    "large": "",
    "lblot": "⦉",
    "lbrace": "{",
    "lbrack": "[",
    "lceil": "⌈",
    "ldots": "…",
    "le": "<",
    "leadsto": "⤳",
    "leftarrow": "←",
    "leftarrowtail": "↢",
    "leftarrowtriangle": "⇽",
    "leftbarharpoon": "⥪",
    "leftharpoondown": "↽",
    "leftharpoonup": "↼",
    "leftleftarrows": "⇇",
    "leftleftharpoons": "⥢",
    "leftmoon": "☾",
    "leftrightarrow": "↔",
    "leftrightarrows": "⇆",
    "leftrightarrowtriangle": "⇿",
    "leftrightharpoon": "⥊",
    "leftrightharpoondown": "⥐",
    "leftrightharpoons": "⇋",
    "leftrightharpoonup": "⥎",
    "leftrightsquigarrow": "↭",
    "leftslice": "⪦",
    "leftsquigarrow": "⇜",
    "leftthreetimes": "⋋",
    "leftupdownharpoon": "⥑",
    "leo": "♌",
    "leq": "≤",
    "leqq": "≦",
    "leqslant": "⩽",
    "lessapprox": "⪅",
    "lessdot": "⋖",
    "lesseqgtr": "⋚",
    "lesseqqgtr": "⪋",
    "lessgtr": "≶",
    "lessim": "≲",
    "lesssim": "≲",
    "lfloor": "⌊",
    "lgroup": "⟮",
    "lhd": "◁",
    "libra": "♎",
    "lightning": "↯",
    "limg": "⦇",
    "ll": "≪",
    "llbracket": "⟦",
    "llcorner": "⌞",
    "llcurly": "⪻",
    "lll": "⋘",
    "lnapprox": "⪉",
    "lneq": "⪇",
    "lneqq": "≨",
    "lnot": "¬",
    "lnsim": "⋦",
    "longleftarrow": "⟵",
    "longleftrightarrow": "⟷",
    "longmapsfrom": "⟻",
    "longmapsto": "⟼",
    "longrightarrow": "⟶",
    "looparrowleft": "↫",
    "looparrowright": "↬",
    "lor": "∨",
    "lozenge": "◊",
    "lrcorner": "⌟",
    "ltimes": "⋉",
    "male": "♂",
    "maltese": "✠",
    "mapsfrom": "↤",
    "mapsto": "↦",
    "measuredangle": "∡",
    "medbullet": "⚫",
    "medcirc": "⚪",
    "mercury": "☿",
    "mho": "℧",
    "mid": "∣",
    "mlcp": "⫛",
    "mod": " mod ",
    "models": "⊧",
    "mp": "∓",
    "mu": "μ",
    "multimap": "⊸",
    "multimapboth": "⧟",
    "multimapdotbothA": "⊶",
    "multimapdotbothB": "⊷",
    "multimapinv": "⟜",
    "nLeftarrow": "⇍",
    "nLeftrightarrow": "⇎",
    "nRightarrow": "⇏",
    "nVDash": "⊯",
    "nVdash": "⊮",
    "nabla": "∇",
    "napprox": "≉",
    "natural": "♮",
    "ncong": "≇",
    "nearrow": "↗",
    "neg": "¬",
    "neptune": "♆",
    "neq": "≠",
    "nequiv": "≢",
    "nexists": "∄",
    "ngeq": "≱",
    "ngtr": "≯",
    "ni": "∋",
    "nleftarrow": "↚",
    "nleftrightarrow": "↮",
    "nleq": "≰",
    "nless": "≮",
    "nmid": "∤",
    "nni": "∌",
    "normalsize": "",
    "not\\in": "∉",
    "not\\ni": "∌",
    "not\\preceq": "⋠",
    "not\\subset": "⊄",
    "not\\subseteq": "⊈",
    "not\\succeq": "⋡",
    "not\\supset": "⊅",
    "not\\supseteq": "⊉",
    "not\\trianglelefteq": "⋬",
    "not\\trianglerighteq": "⋭",
    "not\\vartriangleleft": "⋪",
    "not\\vartriangleright": "⋫",
    "notasymp": "≭",
    "notbackslash": "⍀",
    "notin": "∉",
    "notslash": "⌿",
    "nparallel": "∦",
    "nprec": "⊀",
    "npreceq": "⋠",
    "nrightarrow": "↛",
    "nsim": "≁",
    "nsimeq": "≄",
    "nsqsubseteq": "⋢",
    "nsqsupseteq": "⋣",
    "nsubset": "⊄",
    "nsubseteq": "⊈",
    "nsucc": "⊁",
    "nsucceq": "⋡",
    "nsupset": "⊅",
    "nsupseteq": "⊉",
    "ntriangleleft": "⋪",
    "ntrianglelefteq": "⋬",
    "ntriangleright": "⋫",
    "ntrianglerighteq": "⋭",
    "nu": "ν",
    "nvDash": "⊭",
    "nvdash": "⊬",
    "nwarrow": "↖",
    "odot": "⊙",
    "oiiint": "∰",
    "oiint": "∯",
    "oint": "∮",
    "ointctrclockwise": "∳",
    "omega": "ω",
    "ominus": "⊖",
    "oplus": "⊕",
    "oslash": "⊘",
    "otimes": "⊗",
    "over": "/",
    "overbrace": "⏞",
    "overleftrightarrow": "x⃡",
    "overparen": "⏜",
    "overset?=": "≟",
    "overset{?}{=}": "≟",
    "overset{\\operatorname{def}}{=}": "≝",
    "parallel": "∥",
    "partial": "∂",
    "pencil": "✎",
    "perp": "⊥",
    "pfun": "⇸",
    "phi": "ϕ",
    "pi": "π",
    "pinj": "⤔",
    "pisces": "♓",
    "pitchfork": "⋔",
    "pluto": "♇",
    "pm": "±",
    "pointright": "☞",
    "pounds": "£",
    "prec": "≺",
    "precapprox": "⪷",
    "preccurlyeq": "≼",
    "preceq": "⪯",
    "preceqq": "⪳",
    "precnapprox": "⪹",
    "precnsim": "⋨",
    "precsim": "≾",
    "prime": "′",
    "prod": "∏",
    "propto": "∝",
    "psi": "ψ",
    "psur": "⤀",
    "qoppa": "ϙ",
    "quad": " ",
    "quarternote": "♩",
    "radiation": "☢",
    "rang": "⟫",
    "rangle": "⟩",
    "rarr": "→",
    "rblot": "⦊",
    "rbrace": "}",
    "rbrack": "]",
    "rceil": "⌉",
    "recycle": "♻",
    "rfloor": "⌋",
    "rgroup": "⟯",
    "rhd": "▷",
    "rho": "ρ",
    "rightangle": "∟",
    "rightarrow": "→",
    "rightarrowtail": "↣",
    "rightarrowtriangle": "⇾",
    "rightbarharpoon": "⥬",
    "rightharpoondown": "⇁",
    "rightharpoonup": "⇀",
    "rightleftarrows": "⇄",
    "rightleftharpoon": "⥋",
    "rightleftharpoons": "⇌",
    "rightmoon": "☽",
    "rightrightarrows": "⇉",
    "rightrightharpoons": "⥤",
    "rightslice": "⪧",
    "rightsquigarrow": "⇝",
    "rightthreetimes": "⋌",
    "rightupdownharpoon": "⥏",
    "rimg": "⦈",
    "risingdotseq": "≓",
    "rrbracket": "⟧",
    "rsub": "⩥",
    "rtimes": "⋊",
    "sagittarius": "♐",
    "sampi": "ϡ",
    "saturn": "♄",
    "scorpio": "♏",
    "scriptsize": "",
    "searrow": "↘",
    "second": "″",
    "setminus": "⧵",
    "sharp": "♯",
    "sigma": "σ",
    "sim": "∼",
    "simeq": "≃",
    "sixteenthnote": "♬",
    "skull": "☠",
    "slash": "∕",
    "small": "",
    "smallsetminus": "∖",
    "smalltriangledown": "▿",
    "smalltriangleleft": "◃",
    "smalltriangleright": "▹",
    "smalltriangleup": "▵",
    "smile": "⌣",
    "smiley": "☺",
    "spadesuit": "♠",
    "spddot": "¨",
    "sphat": "^",
    "sphericalangle": "∢",
    "spot": "⦁",
    "sptilde": "~",
    "sqcap": "⊓",
    "sqcup": "⊔",
    "sqint": "⨖",
    "sqrt": "√",
    "sqrt": "√",  # ∛ ∜ - partly special handling below
    "sqrt[3]": "∛",
    "sqrt[4]": "∜",
    "sqsubset": "⊏",
    "sqsubseteq": "⊑",
    "sqsupset": "⊐",
    "sqsupseteq": "⊒",
    "square": "□",
    "sslash": "⫽",
    "star": "⋆",
    "steaming": "☕",
    "stigma": "ϛ",
    "strictfi": "⥼",
    "strictif": "⥽",
    "subset": "⊂",
    "subseteq": "⊆",
    "subseteqq": "⫅",
    "subsetneq": "⊊",
    "subsetneqq": "⫋",
    "succ": "≻",
    "succapprox": "⪸",
    "succcurlyeq": "≽",
    "succeq": "⪰",
    "succeqq": "⪴",
    "succnapprox": "⪺",
    "succnsim": "⋩",
    "succsim": "≿",
    "sum": "∑",
    "sun": "☼",
    "supset": "⊃",
    "supseteq": "⊇",
    "supseteqq": "⫆",
    "supsetneq": "⊋",
    "supsetneqq": "⫌",
    "swarrow": "↙",
    "swords": "⚔",
    "talloblong": "⫾",
    "tau": "τ",
    "taurus": "♉",
    "tcohm": "Ω",
    "textbackslash": "\\",
    "textbar": "|",
    "textbullet": "•",
    "textgreater": ">",
    "textless": "<",
    "textprime": "′",
    "therefore": "∴",
    "theta": "θ",
    "third": "‴",
    "times": "×",
    "tiny": "",
    "to": "→",
    "top": "⊤",
    "triangle": "∆",
    "trianglelefteq": "⊴",
    "triangleq": "≜",
    "trianglerighteq": "⊵",
    "twoheadleftarrow": "↞",
    "twoheadrightarrow": "↠",
    "twonotes": "♫",
    "ulcorner": "⌜",
    "underbar": " ̱",
    "underbrace": "⏟",
    "underleftarrow": "x⃮",
    "underline": " ̲",
    "underparen": "⏝",
    "underrightarrow": "x⃯",
    "uparrow": "↑",
    "updownarrow": "↕",
    "updownarrows": "⇅",
    "updownharpoons": "⥮",
    "upharpoonleft": "↿",
    "upharpoonright": "↾",
    "uplus": "⊎",
    "upsilon": "υ",
    "upuparrows": "⇈",
    "upupharpoons": "⥣",
    "uranus": "♅",
    "urcorner": "⌝",
    "utilde": " ̰",
    "vDash": "⊨",
    "varbeta": "β",
    "varclubsuit": "♧",
    "vardiamondsuit": "♦",
    "varepsilon": "ε",
    "varheartsuit": "♥",
    "varkappa": "ϰ",
    "varnothing": "∅",
    "varointclockwise": "∲",
    "varphi": "φ",
    "varpi": "ϖ",
    "varprod": "⨉",
    "varrho": "ϱ",
    "varsigma": "ς",
    "varspadesuit": "♤",
    "vartheta": "θ",
    "vartriangleleft": "⊲",
    "vartriangleright": "⊳",
    "vdash": "⊢",
    "vdots": "⋮",
    "vee": "∨",
    "veebar": "⊻",
    "vert": "|",
    "virgo": "♍",
    "warning": "⚠",
    "wasylozenge": "⌑",
    "wedge": "∧",
    "widehat=": "≙",
    "widehat{=}": "≙",
    "wp": "℘",
    "wr": "≀",
    "xi": "ξ",
    "yen": "¥",
    "yinyang": "☯",
    "zcmp": "⨟",
    "zeta": "ζ",
    "zhide": "⧹",
    "zpipe": "⨠",
    "zproject": "⨡",
    "|": "‖",
    # Accents XXX these really should be handled specially with diacritics
    # after argument
    "acute": "́",
    "bar": "̄",
    "breve": "̆",
    "check": "̌",
    "ddddot": "⃜",
    "dddot": "⃛",
    "ddot": "̈",
    "ddots": "⋱",
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

mathcal_map: dict[str, str] = {
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

mathfrak_map: dict[str, str] = {
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

mathbb_map: dict[str, str] = {
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


def mathcal_fn(text: str) -> str:
    return "".join(mathcal_map.get(x, x) for x in text)


def mathfrak_fn(text: str) -> str:
    return "".join(mathfrak_map.get(x, x) for x in text)


def mathbb_fn(text: str) -> str:
    return "".join(mathbb_map.get(x, x) for x in text)


def to_math(text: str) -> str:
    """Converts a mathematical formula to ASCII."""
    # print("to_math: {!r}".format(text))
    magic_vec: list[str] = []

    def expand(text: str) -> str:
        while True:
            orig = text
            # formatting with {:c} converts input into character
            text = re.sub(
                r"[{:c}-{:c}]".format(MAGIC_FIRST, MAGIC_LAST),
                lambda m: magic_vec[ord(m.group(0)) - MAGIC_FIRST],
                text,
            )
            if text == orig:
                break
        return text

    def recurse(text: str) -> str:
        def math_magic(
            text: str, left: str, right: str, fn: Callable[[str], str]
        ) -> str:
            regexp_str = r"{}([^{}{}]+){}".format(
                re.escape(left),
                re.escape(left),
                re.escape(right),
                re.escape(right),
            )
            regexp = re.compile(regexp_str)

            def repl(m: re.Match) -> str:
                magic = chr(MAGIC_FIRST + len(magic_vec))
                t = fn(m.group(1)).strip()
                magic_vec.append(t)
                return magic

            while True:
                orig = text
                text = re.sub(regexp, repl, text)
                if text == orig:
                    break
            return text

        def expand_group(v: str) -> str:
            fn: Optional[Callable[[str], str]] = None
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
                    v = "∛"
                elif a == "4":
                    v = "∜"
                else:
                    v = to_superscript(a) + "√"
            elif re.match(r"\\sqrt($|[0-9]|\b)", v):
                v = "√"
            elif re.match(r"\\(frac|binom)($|[0-9]|\b)", v):
                m = re.match(
                    r"\\(frac|binom)\s*(\\[a-zA-Z]+|\\.|.)\s*"
                    r"(\\[a-zA-Z]+|\\.|.)$",
                    v,
                )
                if not m:
                    print("MATH FRAC/BINOM ERROR: {!r}".format(v))
                    return v
                op, a, b = m.groups()
                a = expand_group(a).strip()
                b = expand_group(b).strip()
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
            v = expand(v)
            return v

        parts: list[str] = []
        while True:
            orig = text
            text = math_magic(text, "{", "}", recurse)
            if text == orig:
                break
        for m in re.finditer(
            r"\s+|"
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
            r"[_^]?(\\[a-zA-Z]+\s*|\\.|\w+|.)",
            text,
        ):
            v = m.group(0).strip()
            if not v:
                continue
            v = expand_group(v)
            if v:
                if (
                    parts and parts[-1][-1].isalpha() and v[0] in "0123456789"
                ) or (
                    parts
                    and parts[-1][-1] in "0123456789"
                    and v[0] in "0123456789"
                ):
                    v = " " + v
                parts.append(v)

        text = "".join(parts)
        return text

    text = recurse(text)
    # print("math text final: {!r}".format(text))
    return text


def bold_follows(parts: list[str], i: int) -> bool:
    """Checks if there is a bold (''') in parts after parts[i].  We allow
    intervening italics ('')."""
    parts = parts[i + 1 :]
    for p in parts:
        if not p.startswith("''"):
            continue
        if p.startswith("'''"):
            return True
    return False


def remove_italic_and_bold(text: str) -> str:
    """Based on token_iter in wikitextprocessor"""
    assert isinstance(text, str)
    lines = re.split(r"(\n+)", text)  # Lines and separators
    parts_re = re.compile(r"(''+)")
    new_text_parts = []
    for line in lines:
        parts = re.split(parts_re, line)
        state = 0  # 1=in italic 2=in bold 3=in both
        for i, part in enumerate(parts):
            if part.startswith("''"):
                # This is a bold/italic part.  Scan the rest of the line
                # to determine how it should be interpreted if there are
                # more than two apostrophes.
                if part.startswith("'''''"):
                    if state == 1:  # in italic
                        part = part[5:]
                        state = 2
                    elif state == 2:  # in bold
                        part = part[5:]
                        state = 1
                    elif state == 3:  # in both
                        state = 0
                        part = part[5:]
                    else:  # in nothing
                        part = part[5:]
                        state = 3
                elif part.startswith("'''"):
                    if state == 1:  # in italic
                        if bold_follows(parts, i):
                            part = part[3:]
                            state = 3
                        else:
                            part = part[2:]
                            state = 0
                    elif state == 2:  # in bold
                        part = part[3:]
                        state = 0
                    elif state == 3:  # in both
                        part = part[3:]
                        state = 1
                    else:  # in nothing
                        part = part[3:]
                        state = 2
                elif part.startswith("''"):
                    if state == 1:  # in italic
                        part = part[2:]
                        state = 0
                    elif state == 2:  # in bold
                        part = part[2:]
                        state = 3
                    elif state == 3:  # in both
                        part = part[2:]
                        state = 2
                    else:  # in nothing
                        part = part[2:]
                        state = 1
                if part:
                    new_text_parts.append(part)
                continue
            new_text_parts.append(part)
        new_text_parts.append("\n")
    new_text_parts = new_text_parts[:-1]  # remove last \n
    return "".join(new_text_parts)


# regex to find File/Image link attributes that would mean an image
# is *not* inline
inline_re = re.compile(r"\|\s*(right|left|center|thumb|frame)\s*\|")


url_starts_re = re.compile(
    r"({})".format(r"|".join(URL_STARTS)), flags=re.IGNORECASE
)


def clean_value(
    wxr: WiktextractContext, title: str, no_strip=False, no_html_strip=False
) -> str:
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(title, str)

    def repl_1(m: re.Match) -> str:
        return clean_value(wxr, m.group(1), no_strip=True)

    def repl_exturl(m: re.Match) -> str:
        args = re.split(r"\s+", m.group(1))
        i = 0
        while i < len(args) - 1:
            if not url_starts_re.match(args[i]):
                break
            i += 1
        return " ".join(args[i:])

    def repl_link(m: re.Match) -> str:
        if m.group(2) and m.group(2).lower() in ("file", "image"):
            return ""
        v = m.group(3).split("|")
        return clean_value(wxr, v[0], no_strip=True)

    def repl_link_bars(m: re.Match) -> str:
        lnk = m.group(1)
        if wxr.wtp.file_aliases_re.match(lnk):
            # Handle File / Image / Fichier 'links' here.
            if not inline_re.match(m.group(0)) and "alt" in m.group(0):
                # This image should be inline, so let's print its alt text
                alt_m = re.search(r"\|\s*alt\s*=([^]|]+)(\||\]\])", m.group(0))
                if alt_m is not None:
                    return "[Alt: " + alt_m.group(1) + "]"
            return ""
        # m.group(5) is always the last matching group because you can
        # only access the last matched group; the indexes don't 'grow'
        return clean_value(wxr, m.group(5) or m.group(2) or "", no_strip=True)

    def repl_1_sup(m: re.Match) -> str:
        return to_superscript(clean_value(wxr, m.group(1)))

    def repl_1_sub(m: re.Match) -> str:
        return to_subscript(clean_value(wxr, m.group(1)))

    def repl_1_chem(m: re.Match) -> str:
        return to_chem(clean_value(wxr, m.group(1)))

    def repl_1_math(m: re.Match) -> str:
        v = to_math(m.group(1))
        # print("to_math:", ascii(v))
        return v

    def repl_1_syntaxhighlight(m: re.Match) -> str:
        # Content is preformatted
        return "\n" + m.group(1).strip() + "\n"

    # Remove any remaining templates
    # title = re.sub(r"\{\{[^}]+\}\}", "", title)
    # Remove tables
    title = re.sub(r"(?s)\{\|.*?\|\}", "\n", title)
    # Remove second reference tags (<ref name="ref_name"/>)
    title = re.sub(r"<ref\s+name=\"[^\"]+\"\s*/>", "", title)
    # Remove references (<ref>...</ref>).
    title = re.sub(r"(?is)<ref\b\s*[^>/]*?>\s*.*?</ref\s*>", "", title)
    # Replace <span>...</span> by stripped content without newlines
    title = re.sub(
        r"(?is)<span\b\s*[^>]*?>(.*?)\s*</span\s*>",
        lambda m: re.sub(r"\s+", " ", m.group(1)),
        title,
    )
    # Replace <br/> by comma space (it is used to express alternatives in some
    # declensions)
    title = re.sub(r"(?si)\s*<br\s*/?>\n*", "\n", title)
    # Remove divs with floatright class (generated e.g. by {{ja-kanji|...}})
    title = re.sub(
        r'(?si)<div\b[^>]*?\bclass="[^"]*?\bfloatright\b[^>]*?>'
        r"((<div\b(<div\b.*?</div\s*>|.)*?</div>)|.)*?"
        r"</div\s*>",
        "",
        title,
    )
    # Remove divs with float: attribute
    title = re.sub(
        r'(?si)<div\b[^>]*?\bstyle="[^"]*?\bfloat:[^>]*?>'
        r"((<div\b(<div\b.*?</div\s*>|.)*?</div>)|.)*?"
        r"</div\s*>",
        "",
        title,
    )
    # Remove <sup> with previewonly class (generated e.g. by {{taxlink|...}})
    title = re.sub(
        r'(?si)<sup\b[^>]*?\bclass="[^"<>]*?'
        r"\bpreviewonly\b[^>]*?>"
        r".+?</sup\s*>",
        "",
        title,
    )
    # Remove <strong class="error">...</strong>
    title = re.sub(
        r'(?si)<strong\b[^>]*?\bclass="[^"]*?\berror\b[^>]*?>'
        r".+?</strong\s*>",
        "",
        title,
    )
    # Change <div> and </div> to newlines.  Ditto for tr, li, table, dl, ul, ol
    title = re.sub(r"(?si)</?(div|tr|li|table|dl|ul|ol)\b[^>]*>", "\n", title)
    # Change <dt>, <dd>, </dt> and </dd> into newlines;
    # these generate new rows/lines.
    title = re.sub(r"(?i)</?d[dt]\s*>", "\n", title)
    # Change <td> </td> to spaces.  Ditto for th.
    title = re.sub(r"(?si)</?(td|th)\b[^>]*>", " ", title)
    # Change <sup> ... </sup> to ^
    title = re.sub(r"(?si)<sup\b[^>]*>\s*</sup\s*>", "", title)
    title = re.sub(r"(?si)<sup\b[^>]*>(.*?)</sup\s*>", repl_1_sup, title)
    # Change <sub> ... </sub> to _
    title = re.sub(r"(?si)<sub\b[^>]*>\s*</sup\s*>", "", title)
    title = re.sub(r"(?si)<sub\b[^>]*>(.*?)</sub\s*>", repl_1_sub, title)
    # Change <chem> ... </chem> using subscripts for digits
    title = re.sub(r"(?si)<chem\b[^>]*>(.*?)</chem\s*>", repl_1_chem, title)
    # Change <math> ... </math> using special formatting.
    title = re.sub(r"(?si)<math\b[^>]*>(.*?)</math\s*>", repl_1_math, title)
    # Change <syntaxhighlight> ... </syntaxhighlight> using special formatting.
    title = re.sub(
        r"(?si)<syntaxhighlight\b[^>]*>(.*?)" r"</syntaxhighlight\s*>",
        repl_1_syntaxhighlight,
        title,
    )
    # Remove any remaining HTML tags.
    if not no_html_strip:
        title = re.sub(r"(?s)<[/!a-zA-Z][^>]*>", "", title)
        title = re.sub(r"(?s)</[^>]+>", "", title)
    else:
        # Strip <noinclude/> anyway
        title = re.sub(r"(?si)<noinclude\s*/\s*>", "", title)
    # Replace [...]
    title = re.sub(r"(?s)\[\s*\.\.\.\s*\]", "…", title)
    # Remove http links in superscript
    title = re.sub(r"\^\(\[?(https?:)?//[^]()]+\]?\)", "", title)
    # Remove any edit links to local pages
    title = re.sub(r"\[//[^]\s]+\s+edit\s*\]", "", title)
    # Replace links by their text

    category_ns_data: NamespaceDataEntry
    # XXX "Category" -> config variable for portability
    category_ns_data = wxr.wtp.NAMESPACE_DATA.get("Category", {})  # type: ignore[typeddict-item]
    # Fail if we received empty dict from .get()
    category_ns_names = {category_ns_data["name"]} | set(
        category_ns_data["aliases"]
    )
    category_names_pattern = rf"(?:{'|'.join(category_ns_names)})"
    while True:
        # Links may be nested, so keep replacing until there is no more change.
        orig = title
        title = re.sub(
            rf"(?si)\[\[\s*{category_names_pattern}\s*:\s*([^]]+?)\s*\]\]",
            "",
            title,
        )
        title = re.sub(
            r"(?s)\[\[\s*:?([^]|#<>]+?)\s*(#[^][|<>]*?)?\]\]", repl_1, title
        )
        title = re.sub(
            r"(?s)\[\[\s*(([a-zA-Z0-9]+)\s*:)?\s*([^][#|<>]+?)"
            r"\s*(#[^][|]*?)?\|?\]\]",
            repl_link,
            title,
        )
        title = re.sub(
            r"(?s)\[\[\s*([^][|<>]+?)\s*\|"
            r"\s*(([^][|]|\[[^]]*\])+?)"
            r"(\s*\|\s*(([^][|]|\[[^]]*\])+?))*\s*\]\]",
            repl_link_bars,
            title,
        )
        if title == orig:
            break
    # Replace remaining HTML links by the URL.
    while True:
        orig = title
        title = re.sub(
            r"\[\s*((https?:|mailto:)?//([^][]+?))\s*\]", repl_exturl, title
        )
        if title == orig:
            break

    # Remove italic and bold
    title = remove_italic_and_bold(title)

    # Replace HTML entities
    title = html.unescape(title)
    title = title.replace("\xa0", " ")  # nbsp
    # Remove left-to-right and right-to-left, zero-with characters
    title = re.sub(r"[\u200e\u200f\u200b\u200d\u200c\ufeff]", "", title)
    # Replace whitespace sequences by a single space.
    title = re.sub(r"[ \t\r]+", " ", title)
    title = re.sub(r" *\n+", "\n", title)
    # Eliminate spaces around ellipsis in brackets
    title = re.sub(r"\[\s*…\s*\]", "[…]", title)

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


def clean_template_args(
    wxr: WiktextractContext, ht: TemplateArgs, no_strip=False
) -> dict[str, str]:
    """Cleans all values in a template argument dictionary and returns the
    cleaned dictionary."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(ht, dict)
    return {
        clean_value(wxr, str(k), no_html_strip=True): clean_value(
            wxr, str(v), no_strip=no_strip, no_html_strip=True
        )
        for k, v in ht.items()
    }
