from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.extractor.zh.pronunciation import extract_pronunciation_section
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="zh"
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_homophone_table(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """* [[w:官話|官話]]
** <small>([[w:現代標準漢語|現代標準漢語]])</small>
*** <small>同音詞</small>：<table><tr><th>[展開/摺疊]</th></tr><tr><td><span class="Hani" lang="zh">[[大姑#漢語|大姑]]</span><br><span class="Hani" lang="zh">[[小姑#漢語|小姑]]</span></td></tr></table>
* [[w:晉語|晉語]]
** <small>([[w:太原話|太原話]])</sup></small>
*** <small>[[Wiktionary:國際音標|國際音標]] (老派)</small>：<span class="IPA">/sz̩⁵³/</span>
            """,
        )
        root = self.wxr.wtp.parse("{{zh-pron}}")
        base_data = WordEntry(
            word="大家", lang_code="zh", lang="漢語", pos="noun"
        )
        extract_pronunciation_section(self.wxr, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in base_data.sounds],
            [
                {
                    "homophone": "大姑",
                    "tags": ["Mandarin", "Standard-Chinese"],
                    "raw_tags": ["同音詞"],
                },
                {
                    "homophone": "小姑",
                    "tags": ["Mandarin", "Standard-Chinese"],
                    "raw_tags": ["同音詞"],
                },
                {
                    "ipa": "/sz̩⁵³/",
                    "tags": ["Jin", "Taiyuan", "IPA", "dated"],
                },
            ],
        )

    def test_homophone_template(self):
        self.wxr.wtp.start_page("大家")
        root = self.wxr.wtp.parse("* {{homophones|ja|大矢|大宅|大谷}}")
        base_data = WordEntry(
            word="大家", lang_code="ja", lang="日語", pos="noun"
        )
        extract_pronunciation_section(self.wxr, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in base_data.sounds],
            [
                {"homophone": "大矢"},
                {"homophone": "大宅"},
                {"homophone": "大谷"},
            ],
        )

    def test_en_pron_list(self):
        self.wxr.wtp.start_page("hello")
        self.wxr.wtp.add_page("Template:a", 10, "(美國)")
        root = self.wxr.wtp.parse(
            "* {{a|US}} {{enPR|hĕ-lō'|hə-lō'}}、{{IPA|en|/hɛˈloʊ/|/həˈloʊ/|/ˈhɛloʊ/}}"
        )
        base_data = WordEntry(
            word="hello", lang_code="en", lang="英語", pos="intj"
        )
        extract_pronunciation_section(self.wxr, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in base_data.sounds],
            [
                {"enpr": "hĕ-lō'", "raw_tags": ["美國"]},
                {"enpr": "hə-lō'", "raw_tags": ["美國"]},
                {"ipa": "/hɛˈloʊ/", "raw_tags": ["美國"]},
                {"ipa": "/həˈloʊ/", "raw_tags": ["美國"]},
                {"ipa": "/ˈhɛloʊ/", "raw_tags": ["美國"]},
            ],
        )

    def test_level3_pron_level3_pos(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div><div>
* [[w:官話|官話]]
*:<small>([[w:漢語拼音|拼音]])</small>：<span>[[chōng'ěr]]</span>
</div></div>[[Category:有國際音標的漢語詞|儿04耳00]]""",
        )
        self.wxr.wtp.add_page(
            "Template:zh-verb",
            10,
            "充耳[[Category:漢語詞元|儿04耳00]][[Category:漢語動詞|儿04耳00]]",
        )
        self.wxr.wtp.add_page(
            "Template:head",
            10,
            "充耳[[Category:漢語詞元|儿04耳00]][[Category:漢語名詞|儿04耳00]]",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "充耳",
                """==漢語==
===發音===
{{zh-pron
|m=chōng'ěr
|cat=v,n
}}

===動詞===
{{zh-verb}}

# [[塞住]][[耳朵]]

===名詞===
{{head|zh|名詞}}

# 古[[冠冕]]旁的[[瑱]]玉，因其[[下垂]]及耳，而得名""",
            ),
            [
                {
                    "categories": [
                        "有國際音標的漢語詞",
                        "漢語詞元",
                        "漢語動詞",
                    ],
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "verb",
                    "pos_title": "動詞",
                    "senses": [{"glosses": ["塞住耳朵"]}],
                    "sounds": [
                        {"zh_pron": "chōng'ěr", "tags": ["Mandarin", "Pinyin"]}
                    ],
                    "word": "充耳",
                },
                {
                    "categories": [
                        "有國際音標的漢語詞",
                        "漢語詞元",
                        "漢語名詞",
                    ],
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [
                        {"glosses": ["古冠冕旁的瑱玉，因其下垂及耳，而得名"]}
                    ],
                    "sounds": [
                        {"zh_pron": "chōng'ěr", "tags": ["Mandarin", "Pinyin"]}
                    ],
                    "word": "充耳",
                },
            ],
        )

    def test_level3_pron_level4_pos(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div><div>
* [[w:官話|官話]]
*:<small>([[w:漢語拼音|拼音]])</small>：<span>[[{{{m}}}]]</span>
</div></div>""",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "大家",
                """==漢語==
===發音1===
{{zh-pron
|m=dàjiā, dà'ā
|cat=n
}}

====名詞====

# [[眾人]]，某個[[範圍]]中[[所有]]的[[人]]

===發音2===
{{zh-pron
|m=dàjiā
|cat=n
}}

====名詞====

# [[卿大夫]]之[[家]]

===發音3===
{{zh-pron
|m=dàgū
|cat=n
}}

====名詞====

# 對[[女子]]的[[尊稱]]""",
            ),
            [
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [{"glosses": ["眾人，某個範圍中所有的人"]}],
                    "sounds": [
                        {
                            "zh_pron": "dàjiā",
                            "tags": ["Mandarin", "Pinyin"],
                        },
                        {
                            "zh_pron": "dà'ā",
                            "tags": ["Mandarin", "Pinyin"],
                        },
                    ],
                    "word": "大家",
                },
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [{"glosses": ["卿大夫之家"]}],
                    "sounds": [
                        {"zh_pron": "dàjiā", "tags": ["Mandarin", "Pinyin"]}
                    ],
                    "word": "大家",
                },
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [{"glosses": ["對女子的尊稱"]}],
                    "sounds": [
                        {"zh_pron": "dàgū", "tags": ["Mandarin", "Pinyin"]}
                    ],
                    "word": "大家",
                },
            ],
        )

    def test_split_tag(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """* [[w:莆仙語|莆仙語]] <small>([[Wiktionary:關於漢語/莆仙語|莆仙話拼音]])：</small><span>doeng<sup>1</sup> gorh<sup>6</sup> / dyoeng<sup>1</sup> gorh<sup>6</sup></span>
* [[w:閩南語|閩南語]]
** <small>([[w:泉漳片|泉漳話]]：[[w:廈門話|廈門]]、[[w:泉州話|泉州]]、[[w:漳州話|漳州]]、[[w:臺灣話|臺灣話]]（常用）、[[w:檳城福建話|檳城]])</small>
*** <small>[[w:白話字|白話字]]</small>：<span><span class="form-of poj-form-of" lang="nan-hbl">[[Tiong-kok#泉漳話|Tiong-kok]]</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "中國",
            """==漢語==
===發音===
{{zh-pron
|m=Zhōngguó
|cat=pn,n
}}
===專有名詞===
# gloss""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "tags": ["Puxian-Min", "Pouseng-Ping'ing"],
                    "zh_pron": "doeng¹ gorh⁶",
                },
                {
                    "tags": ["Puxian-Min", "Pouseng-Ping'ing"],
                    "zh_pron": "dyoeng¹ gorh⁶",
                },
                {
                    "tags": [
                        "Min-Nan",
                        "Hokkien",
                        "Xiamen",
                        "Quanzhou",
                        "Zhangzhou",
                        "Taiwanese",
                        "Penang",
                        "general",
                        "Phak-fa-su",
                    ],
                    "zh_pron": "Tiong-kok",
                },
            ],
        )

    def test_not_split_text_in_parentheses(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="發音">
* [[w:官話|官話]]
*: <small>([[w:東干語|東干語]]，[[w:东干语#東干語拼寫法|西里爾字母]]和[[Wiktionary:東干語轉寫|維基詞典轉寫]])</small>：<span style="font-family: Consolas, monospace;">[[даҗя#東干語|даҗя]] (daži͡a, III-I)</span>
* [[w:閩南語|閩南語]]
** <small>([[w:泉漳片|泉漳話]]：[[w:廈門話|廈門]]、[[w:泉州話|泉州]]、[[w:新加坡福建話|新加坡]])</small>
*** <small>[[Wiktionary:國際音標|國際音標]] ([[w:廈門話|廈門]], [[w:新加坡福建話|新加坡]])</small>：<span class="IPA">/tai̯²²⁻²¹ ke⁴⁴/</span>
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "大家",
            """==漢語==
===發音1===
{{zh-pron
|m=dàjiā,dà'ā,2nb=口語
|cat=n
}}
====名詞====
# [[眾人]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "tags": [
                        "Mandarin",
                        "Dongan",
                        "Cyrillic",
                        "Wiktionary-specific",
                    ],
                    "zh_pron": "даҗя (daži͡a, III-I)",
                },
                {
                    "ipa": "/tai̯²²⁻²¹ ke⁴⁴/",
                    "tags": [
                        "Min-Nan",
                        "Hokkien",
                        "Xiamen",
                        "Quanzhou",
                        "Singapore",
                        "IPA",
                    ],
                },
            ],
        )

    def test_homophone_table_character_forms(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div><div class="vsSwitcher" data-toggle-category="發音">
* [[w:粵語|粵語]]
** <small>([[w:粵語|標準粵語]]，[[w:廣州話|廣州]]–[[w:香港粵語|香港話]])</small>
*** <small>同音詞</small>: <table class="wikitable mw-collapsible mw-collapsed"><tr><th></th></tr><tr><td><div style="float: right; clear: right;"><sup><span class="plainlinks">[//zh.wiktionary.org/w/index.php?title=Module%3AYue-pron%2Fhom&action=edit edit]</span></sup></div><div style="visibility:hidden; float:left"><sup><span style="color:#FFF">edit</span></sup></div><span class="Hant" lang="yue">-{<!-- -->[[廚子#粵語|-{廚子}-]]}-</span><span class="Zsym mention" style="font-size:100%;">／</span><span class="Hans" lang="yue">-{<!-- -->[[厨子#粵語|-{厨子}-]]}-</span></td></tr></table>[[Category:有同音詞的粵語詞]]</div></div></div>
""",
        )
        data = parse_page(
            self.wxr,
            "錘子",
            """==漢語==
===發音===
{{zh-pron
|m=chuízi
|m-s=cui2zi3
|c=ceoi4 zi2
|cat=n,pron,det
}}

===名詞===

# 由[[金屬]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "homophone": "廚子",
                    "raw_tags": ["同音詞"],
                    "tags": [
                        "Traditional-Chinese",
                        "Cantonese",
                        "Standard-Cantonese",
                        "Guangzhou",
                        "Hong Kong",
                    ],
                },
                {
                    "homophone": "厨子",
                    "raw_tags": ["同音詞"],
                    "tags": [
                        "Simplified-Chinese",
                        "Cantonese",
                        "Standard-Cantonese",
                        "Guangzhou",
                        "Hong Kong",
                    ],
                },
            ],
        )

    def test_zh_pron_arrow(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="發音">
* [[w:閩東語|閩東語]] <small>([[Wiktionary:關於漢語/閩東語|平話字]])</small>：<span style="font-family: Consolas, monospace;">mĕ̤k<sup>→maĕ̤h</sup>-lê / mĕk<sup>→mĕh</sup>-lê</span>
* [[w:吳語|吳語]] <small>([[w:上海話|上海]]，[[Wiktionary:關於漢語/吳語|吳語學堂拼音]])</small>：<span class="zhpron-monospace"><sup>5</sup>meq-li; <sup>5</sup>moq-li</span><span class="vsToggleElement" style="float: right;"></span>
<div class="vsHide" style="clear:right;">
<hr>
* [[w:官話|官話]]
** <small>([[w:現代標準漢語|現代標準漢語]])</small><sup><small><abbr title="添加官話同音詞"><span class="plainlinks">[//zh.wiktionary.org/w/index.php?title=Module%3AZh%2Fdata%2Fcmn-hom%2F2&action=edit +]</span></abbr></small></sup>
*** <small>[[w:漢語拼音|拼音]]</small>：<span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace"><span class="Latn" lang="cmn">-{<!-- -->[[mòlì#官話|-{mòlì}-]]}-</span> → mò<span style="background-color:#F5DEB3">li</span> <small>（輕尾聲異讀）</small></span>
*** <small>[[w:注音符號|注音]]</small>：<span lang="cmn-Bopo" class="Bopo">ㄇㄛˋ ㄌㄧˋ → ㄇㄛˋ ˙ㄌㄧ</span> <small>（輕尾聲異讀）</small>
*** <small>[[w:漢語西里爾字母轉寫系統|西里爾字母轉寫]]</small>：<span style="font-family: Consolas, monospace;"><span lang="cmn-Cyrl">моли</span> <span lang="cmn-Latn">(moli)</span></span>
*** <small>漢語[[Wiktionary:國際音標|國際音標]] <sup>([[維基詞典:漢語發音表記|幫助]])</sup></small>：<span class="IPA">/mu̯ɔ⁵¹⁻⁵³ li⁵¹/ → /mu̯ɔ⁵¹ li¹/</span>[[Category:有輕聲異讀的官話詞|mòlì]]
* [[w:閩東語|閩東語]]
** <small>([[w:福州話|福州話]])</small>
*** <small>[[Wiktionary:國際音標|國際音標]] <sup>([[w:福州話|幫助]])</sup></small>：<span class="IPA">/møyʔ⁵⁻²¹ l̃ɛi²⁴²/, /mɛiʔ⁵⁻²¹ l̃ɛi²⁴²/</span>
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "茉莉",
            """==漢語==
===發音===
{{zh-pron
|m=mòlì,tl=y
|cat=n
}}

===名詞===

# [[植物]]名。""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "tags": ["Min-Dong", "Foochow-Romanized"],
                    "zh_pron": "mĕ̤k^(→maĕ̤h)-lê",
                },
                {
                    "tags": ["Min-Dong", "Foochow-Romanized"],
                    "zh_pron": "mĕk^(→mĕh)-lê",
                },
                {"tags": ["Wu", "Shanghai", "Wugniu"], "zh_pron": "⁵meq-li"},
                {"tags": ["Wu", "Shanghai", "Wugniu"], "zh_pron": "⁵moq-li"},
                {
                    "tags": ["Mandarin", "Standard-Chinese", "Pinyin"],
                    "zh_pron": "mòlì",
                },
                {
                    "tags": [
                        "Mandarin",
                        "Standard-Chinese",
                        "Pinyin",
                        "toneless-final-syllable-variant",
                    ],
                    "zh_pron": "mòli",
                },
                {
                    "tags": ["Mandarin", "Standard-Chinese", "Bopomofo"],
                    "zh_pron": "ㄇㄛˋ ㄌㄧˋ",
                },
                {
                    "tags": [
                        "Mandarin",
                        "Standard-Chinese",
                        "Bopomofo",
                        "toneless-final-syllable-variant",
                    ],
                    "zh_pron": "ㄇㄛˋ ˙ㄌㄧ",
                },
                {
                    "roman": "moli",
                    "tags": ["Mandarin", "Standard-Chinese", "Cyrillic"],
                    "zh_pron": "моли",
                },
                {
                    "ipa": "/mu̯ɔ⁵¹⁻⁵³ li⁵¹/",
                    "tags": ["Mandarin", "Standard-Chinese", "Sinological-IPA"],
                },
                {
                    "ipa": "/mu̯ɔ⁵¹ li¹/",
                    "tags": ["Mandarin", "Standard-Chinese", "Sinological-IPA"],
                },
                {
                    "ipa": "/møyʔ⁵⁻²¹ l̃ɛi²⁴²/",
                    "tags": ["Min-Dong", "Fuzhou", "IPA"],
                },
                {
                    "ipa": "/mɛiʔ⁵⁻²¹ l̃ɛi²⁴²/",
                    "tags": ["Min-Dong", "Fuzhou", "IPA"],
                },
            ],
        )

    def test_zh_pron_phonetic(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="發音">
<div class="vsHide" style="clear:right;">
<hr>
* [[Wiktionary:關於漢語/莆仙語|莆仙語]]
** <small>([[w:莆田話|莆田]])</small>
*** <small>[[Wiktionary:關於漢語/莆仙語|莆仙話拼音]]</small>：<span class="zhpron-monospace">ging<sup>1</sup> li<sup>3</sup></span><span class="zhpron-monospace"> [<small>實際讀音</small>：ging<sup>5</sup> li<sup>3</sup>]</span>
</div></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "經理",
            """==漢語==
===發音===
{{zh-pron
|m=jīnglǐ
|cat=n,v
}}
===名詞===
# [[公司]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "tags": ["Puxian-Min", "Putian", "Pouseng-Ping'ing"],
                    "zh_pron": "ging¹ li³",
                },
                {
                    "tags": [
                        "Puxian-Min",
                        "Putian",
                        "Pouseng-Ping'ing",
                        "phonetic",
                    ],
                    "zh_pron": "ging⁵ li³",
                },
            ],
        )

    def test_zh_pron_pinyin_erhua_phonetic(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron""><div class="vsSwitcher" data-toggle-category="發音">
<div class="vsHide" style="clear:right;">
<hr>
* [[w:官話|官話]]
** <small>([[w:現代標準漢語|現代標準漢語]], [[w:兒化|兒化]]) (<span class="Hant" lang="cmn">-{<!-- -->[[一丁點兒#官話|-{一丁點兒}-]]}-</span><span class="Zsym mention" style="font-size:100%;">／</span><span class="Hans" lang="cmn">-{<!-- -->[[一丁点儿#官話|-{一丁点儿}-]]}-</span>)</small><sup><small><abbr title="添加官話同音詞"><span class="plainlinks">[//zh.wiktionary.org/w/index.php?title=Module%3AZh%2Fdata%2Fcmn-hom%2F4&action=edit +]</span></abbr></small></sup>
*** <small>[[w:漢語拼音|拼音]]</small>：<span class="form-of pinyin-t-form-of transliteration-一丁点" lang="cmn" class="zhpron-monospace"><span class="Latn" lang="cmn">-{<!-- -->[[yīdīngdiǎnr#官話|-{yīdīngdiǎnr}-]]}-</span> [實際讀音：<span style="background-color:#F5DEB3">yì</span>dīngdiǎnr][[Category:有一字而變調為第四聲的官話詞]]</span>
</div></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "一丁點",
            """==漢語==
===發音===
{{zh-pron
|m=一dīngdiǎn,er=y
|c=jat1 ding1 dim2
|cat=a
}}
===形容詞===
# 比喻[[稀少]]、極[[微小]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "raw_tags": ["一丁點兒／一丁点儿"],
                    "tags": ["Mandarin", "Standard-Chinese", "Erhua", "Pinyin"],
                    "zh_pron": "yīdīngdiǎnr",
                },
                {
                    "raw_tags": ["一丁點兒／一丁点儿"],
                    "tags": [
                        "Mandarin",
                        "Standard-Chinese",
                        "Erhua",
                        "Pinyin",
                        "phonetic",
                    ],
                    "zh_pron": "yìdīngdiǎnr",
                },
            ],
        )

    def test_zh_pron_unclosed_parentheses(self):
        # https://zh.wiktionary.org/w/index.php?title=Module:Hak-pron&diff=prev&oldid=9372037
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="發音">
* [[w:客家語|客家語]]
*: <small>([[w:海陸客語|海陸]]，[[w:客家語拼音方案|客家語拼音]]</small>：<span class="zhpron-monospace">rhid tin<sup>˖</sup></span></div></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "一丁點",
            """==漢語==
===發音===
{{zh-pron
|h=pfs=yit-thin;hrs=h:rhid tin˖
|cat=a,adv
}}
===形容詞===
# [[規定]]的；[[確定]]不變的""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "raw_tags": ["(海陸，客家語拼音"],
                    "tags": ["Hakka"],
                    "zh_pron": "rhid tin^˖",
                }
            ],
        )
