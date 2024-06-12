import unicodedata
import re

hiero_phoneme_map: dict[str, str] = {
    "mSa": "A12",
    "xr": "A15",
    "Xrd": "A17",
    "sr": "A21",
    "mniw": "A33",
    "qiz": "A38",
    "iry": "A47",
    "Sps": "A50",
    "Spsi": "A51",

    "msi": "B3",

    "mAat": "C10",
    "HH": "C11",
    "DHwty": "C3",
    "Xnmw": "C4",
    "inpw": "C6",
    "stX": "C7",
    "mnw": "C8",

    "tp": "D1",
    "WDAt": "D10",
    #"R": "D153",
    "fnD": "D19",
    "Hr": "D2",
    "r": "D21",
    "rA": "D21",
    "spt": "D24",
    "spty": "D25",
    "mnD": "D27",
    "kA": "D28",
    "Sny": "D3",
    "aHA": "D34",
    "a": "D36",
    "ir": "D4",
    "Dsr": "D45",
    "d": "D46",
    "Dba": "D50",
    "mt": "D52",
    "gH": "D56",
    "gHs": "D56",
    "rd": "D56",
    "sbq": "D56",
    "b": "D58",
    "ab": "D59",
    "wab": "D60",
    "sAH": "D61",
    "rmi": "D9",

    "zAb": "E17",
    "mAi": "E22",
    "l": "E23",
    "rw": "E23",
    "Aby": "E24",
    "wn": "E34",
    "zzmt": "E6",

    "wsr": "F12",
    "wp": "F13",
    "db": "F16",
    "Hw": "F18",
    "bH": "F18",
    "ns": "F20",
    "DrD": "F21",
    "idn": "F21",
    "msDR": "F21",
    "sDm": "F21",
    "kfA": "F22",
    "pH": "F22",
    "xpS": "F23",
    "wHm": "F25",
    "Xn": "F26",
    "sti": "F29",
    "Sd": "F30",
    "ms": "F31",
    "X": "F32",
    "sd": "F33",
    "ib": "F34",
    "nfr": "F35",
    "zmA": "F36",
    "imAx": "F39",
    "HAt": "F4",
    "Aw": "F40",
    "spr": "F42",
    "isw": "F44",
    "iwa": "F44",
    "pXr": "F46",
    "qAb": "F46",
    "SsA": "F5",

    "A": "G1",
    "mwt": "G14",
    "nbty": "G16",
    "m": "G17",
    "mm": "G18",
    "AA": "G2",
    "nH": "G21",
    "Db": "G22",
    "rxyt": "G23",
    "Ax": "G25",
    "dSr": "G27",
    "gm": "G28",
    "bA": "G29",
    "baHi": "G32",
    "aq": "G35",
    "wr": "G36",
    "nDs": "G37",
    "gb": "G38",
    "zA": "G39",
    "tyw": "G4",
    "pA": "G40",
    "xn": "G41",
    "wSA": "G42",
    "w": "G43",
    "ww": "G44",
    "mAw": "G46",
    "TA": "G47",
    "snD": "G54",

    "pq": "H2",
    "wSm": "H2",
    "pAq": "H3",
    "nr": "H4",
    "Sw": "H6",

    "aSA": "I1",
    "D": "I10",
    "DD": "I11",
    "Styw": "I2",
    "mzH": "I3",
    "sbk": "I4",
    "sAq": "I5",
    "km": "I6",
    "Hfn": "I8",
    "f": "I9",

    "in": "K1",
    "ad": "K3",
    "XA": "K4",
    "bz": "K5",
    "nSmt": "K6",

    "xpr": "L1",
    "bit": "L2",
    "srqt": "L7",

    "iAm": "M1",
    "wdn": "M11",
    "xA": "M12",
    "1000": "M12",
    "wAD": "M13",
    "HA": "M16",
    "i": "M17",
    "ii": "M18",
    "Hn": "M2",
    "sxt": "M20",
    "sm": "M21",
    "nn": "M22A",
    "sw": "M23",
    "rsw": "M24",
    "Sma": "M26",
    "nDm": "M29",
    "xt": "M3",
    "bnr": "M30",
    "bdt": "M34",
    "Dr": "M36",
    "rnp": "M4",
    "iz": "M40",
    "tr": "M6",
    "SA": "M8",
    "zSn": "M9",

    "pt": "N1",
    "Abd": "N11",
    "iaH": "N11",
    "dwA": "N14",
    "sbA": "N14",
    "dwAt": "N15",
    "tA": "N16",
    "iw": "N18",
    "wDb": "N20",
    "spAt": "N24",
    "xAst": "N25",
    "Dw": "N26",
    "Axt": "N27",
    "xa": "N28",
    "q": "N29",
    "iAt": "N30",
    "n": "N35",
    "mw": "N35A",
    "S": "N37",
    "iAdt": "N4",
    "idt": "N4",
    "Sm": "N40",
    "id": "N41",
    "hrw": "N5",
    "ra": "N5",
    "zw": "N5",
    "Hnmmt": "N8",
    "pzD": "N9",

    "pr": "O1",
    "aH": "O11",
    "wsxt": "O15",
    "kAr": "O18",
    "zH": "O22",
    "txn": "O25",
    "iwn": "O28",
    "aA": "O29",
    "zxnt": "O30",
    "z": "O34",
    "zb": "O35",
    "inb": "O36",
    #"qnbt": "O38A",
    "h": "O4",
    "Szp": "O42",
    "ipt": "O45",
    "nxn": "O47",
    "niwt": "O49",
    "zp": "O50",
    "Snwt": "O51",
    "Hwt": "O6",

    "wHa": "P4",
    "TAw": "P5",
    "nfw": "P5",
    "aHa": "P6",
    "xrw": "P8",

    "st": "Q1",
    "wz": "Q2",
    "p": "Q3",
    "qrsw": "Q6",

    "xAt": "R1",
    "xAwt": "R1",
    "Dd": "R11",
    "dd": "R11",
    "imnt": "R14",
    "iAb": "R15",
    "wx": "R16",
    "xm": "R22",
    "Htp": "R4",
    "kAp": "R5",
    "kp": "R5",
    "snTr": "R7",
    "nTr": "R8",
    #"nTrw": "R8A",
    "bd": "R9",

    "HDt": "S1",
    "N": "S3",
    "dSrt": "S3",
    "sxmty": "S6",
    "xprS": "S7",
    "Atf": "S8",
    "Swty": "S9",
    "mDH": "S10",
    "wsx": "S11",
    "nbw": "S12",
    "THn": "S15",
    "tHn": "S15",
    "mnit": "S18",
    "sDAw": "S19",
    "xtm": "S20",
    "sT": "S22",
    "dmD": "S23",
    "Tz": "S24",
    "Sndyt": "S26",
    "mnxt": "S27",
    "s": "S29",
    "sf": "S30",
    "siA": "S32",
    "Tb": "S33",
    "anx": "S34",
    "Swt": "S35",
    "xw": "S37",
    "HqA": "S38",
    "awt": "S39",
    "wAs": "S40",
    "Dam": "S41",
    "abA": "S42",
    "sxm": "S42",
    "xrp": "S42",
    "md": "S43",
    "Ams": "S44",
    "nxxw": "S45",

    "pD": "T10",
    "sXr": "T11",
    "zin": "T11",
    "zwn": "T11",
    "Ai": "T12",
    "Ar": "T12",
    "rwD": "T12",
    "rwd": "T12",
    "rs": "T13",
    "qmA": "T14",
    "wrrt": "T17",
    "Sms": "T18",
    "qs": "T19",
    "wa": "T21",
    "sn": "T22",
    "iH": "T24",
    "DbA": "T25",
    "Xr": "T28",
    "nmt": "T29",
    "HD": "T3",
    "sSm": "T31",
    "nm": "T34",
    "HDD": "T6",
    "pd": "T9",

    "mA": "U1",
    "it": "U10",
    "HqAt": "U11",
    "Sna": "U13",
    "hb": "U13",
    "tm": "U15",
    "biA": "U16",
    "grg": "U17",
    "stp": "U21",
    "mnx": "U22",
    "Ab": "U23",
    "Hmt": "U24",
    "wbA": "U26",
    "DA": "U28",
    "rtH": "U31",
    "zmn": "U32",
    "ti": "U33",
    "xsf": "U34",
    "Hm": "U36",
    "mxAt": "U38",
    "mr": "U6",

    "100": "V1",
    "arq": "V12",
    "T": "V13",
    "iTi": "V15",
    "TmA": "V19",
    "XAr": "V19",
    "mDt": "V19",
    "sTA": "V2",
    "10": "V20",
    "mD": "V20",
    "mH": "V22",
    "wD": "V24",
    "aD": "V26",
    "H": "V28",
    "sk": "V29",
    "wAH": "V29",
    "sTAw": "V3",
    "nb": "V30",
    "k": "V31",
    "msn": "V32",
    "sSr": "V33",
    "idr": "V37",
    "wA": "V4",
    "snT": "V5",
    "sS": "V6",
    "Sn": "V7",

    "iab": "W10",
    "g": "W11",
    "nzt": "W11",
    "Hz": "W14",
    "xnt": "W17",
    "mi": "W19",
    "bAs": "W2",
    "Hnqt": "W22",
    "nw": "W24",
    "ini": "W25",
    "Hb": "W3",
    "Xnm": "W9",

    "t": "X1",
    "di": "X8",
    "rdi": "X8",

    "mDAt": "Y1",
    "mnhd": "Y3",
    "zS": "Y3",
    "mn": "Y5",
    "ibA": "Y6",
    "zSSt": "Y8",

    "imi": "Z11",
    "y": "Z4",
    "W": "Z7",

    "x": "AA1",
    "mAa": "AA11",
    "gs": "AA13",
    "im": "AA15",
    "M": "A15",
    "sA": "AA17",
    "apr": "AA20",
    "wDa": "AA21",
    "nD": "AA27",
    "qd": "AA28",
    "Xkr": "AA30",
    "Hp": "AA5",
    "qn": "AA8",
}

hiero_map: dict[str, str] = {
    "H_SPACE" : "\u00a0",
    ".": " ",
    "..": "\u2003",
}

# Add unicode codes to map
for i in range(0x13000, 0x1342F):
    ch = chr(i)
    name = unicodedata.name(ch)
    g = name.split()[-1]
    m = re.match(r"([a-zA-Z]+)(\d+[a-zA-Z]*)$", g)
    assert m

    prefix, suffix = m.groups()
    while len(suffix) >= 2 and suffix[0] == "0":
        suffix = suffix[1:]
    g = prefix + suffix
    hiero_map[g] = ch


# Map phonemes to unicode characters
for name, g in hiero_phoneme_map.items():
    if g not in hiero_map:
        print("Phoneme {} maps to {} which is not in hiero_map!".format(name, g))
        raise RuntimeError("Phoneme {} maps to unrecognized {}".format(name, g))

    hiero_map[name] = hiero_map[g]

def convert_asterisk(text: str) -> str:
    tokens = text.split("*")
    print("asterisk tokens:", tokens)
    result = []
    for token in tokens:
        if token in hiero_map:
            result.append(hiero_map[token])
        else:
            print("Unhandled token: {!r}".format(token))
            result.append(token)
    v = "\U00013431".join(result)
    return v

def convert_colon(text: str) -> str:
    tokens = text.split(":")
    print("colon tokens:", tokens)
    result = []
    for token in tokens:
        v = convert_asterisk(token)
        if len(v) > 1 and len(tokens) > 1:
            v = "\U00013437" + v + "\U00013438"
        result.append(v)
    return "\U00013430".join(result)

def convert_hiero(text: str) -> str:
    lst = list(m.group(0) for m in re.finditer(
        r"\s+|\s*-\s*|\s*!\s*|[a-zA-Z0-9*:_]+|.", text))
    result = []
    for x in lst:
        x = x.strip()
        if not x or x == "-":
            continue
        if x == "!":
            result.append("\n")
            continue
        v = convert_colon(x)
        if len(v) > 1 and len(lst) > 1:
            v = "\U00013437" + v + "\U00013438"
        result.append(v)
    return "".join(result)
