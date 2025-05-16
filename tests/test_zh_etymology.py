from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.etymology import extract_etymology_section
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNote(TestCase):
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

    def test_zh_x(self):
        self.wxr.wtp.start_page("一刻千金")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<div class="vsSwitcher" data-toggle-category="usage examples" style="border-left: 1px solid #930; border-left-width: 2px; padding-left: 0.8em;"><dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[春宵#漢語|春宵]][[一刻#漢語|<b>一刻</b>]][[直#漢語|直]][[千金#漢語|<b>千金</b>]]，[[花#漢語|花]][[有#漢語|有]][[清香#漢語|清香]][[月#漢語|月]][[有#漢語|有]][[陰#漢語|陰]]。<!-- -->}-</span><span class="vsHide"> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:繁体中文|繁體]]&#93;</span></span><span class="vsToggleElement" style="color:darkgreen; font-size:x-small;padding-left:10px"></span><hr><span class="vsHide"><span lang="zh-Hans" class="Hans">-{<!-- -->[[春宵#漢語|春宵]][[一刻#漢語|<b>一刻</b>]][[直#漢語|直]][[千金#漢語|<b>千金</b>]]，[[花#漢語|花]][[有#漢語|有]][[清香#漢語|清香]][[月#漢語|月]][[有#漢語|有]][[阴#漢語|阴]]。<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:简体中文|簡體]]&#93;</span></span><dd><span class="vsHide"><small>出自：宋．蘇軾《春夜》</small></span></dd><dd><span class="vsHide"><span lang="zh-Latn" style="color:#404D52"><i>Chūnxiāo <b>yīkè</b> zhí <b>qiānjīn</b>, huā yǒu qīngxiāng yuè yǒu yīn.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></span></dd><dd>春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。</dd></dl>[[Category:有引文的文言文詞]]</div>""",  # noqa: E501
        )
        root = self.wxr.wtp.parse("""===詞源===
源自宋．[[w:蘇軾|蘇軾]]《春夜》詩：
{{zh-x|春宵 '''一刻''' 直 '''千金'''，花 有 清香 月 有 陰。|春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。|CL|ref=宋．蘇軾《春夜》|collapsed=y}}""")  # noqa: E501
        base_data = WordEntry(
            lang="漢語", lang_code="zh", word="一刻千金", pos="phrase"
        )
        extract_etymology_section(
            self.wxr, [base_data], base_data, root.children[0]
        )
        self.assertEqual(base_data.etymology_text, "源自宋．蘇軾《春夜》詩：")
        self.assertEqual(
            [
                e.model_dump(exclude_defaults=True)
                for e in base_data.etymology_examples
            ],
            [
                {
                    "ref": "宋．蘇軾《春夜》",
                    "tags": [
                        "Pinyin",
                        "Classical Chinese",
                        "Traditional Chinese",
                    ],
                    "text": "春宵一刻直千金，花有清香月有陰。",
                    "bold_text_offsets": [(2, 4), (5, 7)],
                    "roman": "Chūnxiāo yīkè zhí qiānjīn, huā yǒu qīngxiāng yuè yǒu yīn.",
                    "bold_roman_offsets": [(9, 13), (18, 25)],
                    "translation": "春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。",
                },
                {
                    "ref": "宋．蘇軾《春夜》",
                    "tags": [
                        "Pinyin",
                        "Classical Chinese",
                        "Simplified Chinese",
                    ],
                    "text": "春宵一刻直千金，花有清香月有阴。",
                    "bold_text_offsets": [(2, 4), (5, 7)],
                    "roman": "Chūnxiāo yīkè zhí qiānjīn, huā yǒu qīngxiāng yuè yǒu yīn.",
                    "bold_roman_offsets": [(9, 13), (18, 25)],
                    "translation": "春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。",
                },
            ],
        )

    def test_zh_x_in_list(self):
        self.wxr.wtp.start_page("焚膏繼晷")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<div class="vsSwitcher" data-toggle-category="usage examples" style="border-left: 1px solid #930; border-left-width: 2px; padding-left: 0.8em;"><dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[焚#漢語|<b>焚]][[膏油#漢語|膏</b>油]][[以#漢語|以]][[繼#漢語|<b>繼]][[晷#漢語|晷</b>]]，[[恆#漢語|恆]][[兀兀#漢語|兀兀]][[以#漢語|以]][[窮#漢語|窮]][[年#漢語|年]]。<!-- -->}-</span><span class="vsHide"> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:繁体中文|繁體]]&#93;</span></span><span class="vsToggleElement" style="color:darkgreen; font-size:x-small;padding-left:10px"></span><hr><span class="vsHide"><span lang="zh-Hans" class="Hans">-{<!-- -->[[焚#漢語|<b>焚]][[膏油#漢語|膏</b>油]][[以#漢語|以]][[继#漢語|<b>继]][[晷#漢語|晷</b>]]，[[恒#漢語|恒]][[兀兀#漢語|兀兀]][[以#漢語|以]][[穷#漢語|穷]][[年#漢語|年]]。<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:简体中文|簡體]]&#93;</span></span><dd><span class="vsHide"><small>出自：'''813'''年，[[w:韓愈|韓愈]]《[[s:進學解|進學解]]》</small></span></dd><dd><span class="vsHide"><span lang="zh-Latn" style="color:#404D52"><i><b>Fén gāo</b>yóu yǐ <b>jì guǐ</b>, héng wùwù yǐ qióng nián.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></span></dd><dd>燃燒燈油夜以繼日，終年孜孜不倦刻苦用功。</dd></dl>[[Category:有引文的文言文詞]]</div>""",  # noqa: E501
        )
        root = self.wxr.wtp.parse("""===詞源===
出自唐·韓愈《[[s:進學解|進學解]]》：
: {{zh-x|'''焚 膏'''油 以 '''繼 晷'''，恆 兀兀 以 窮 年。|燃燒燈油夜以繼日，終年孜孜不倦刻苦用功。|CL|ref='''813'''年，{{w|韓愈}}《[[s:進學解|進學解]]》|collapsed=y}}""")  # noqa: E501
        base_data = WordEntry(
            lang="漢語", lang_code="zh", word="焚膏繼晷", pos="phrase"
        )
        extract_etymology_section(
            self.wxr, [base_data], base_data, root.children[0]
        )
        self.assertEqual(base_data.etymology_text, "出自唐·韓愈《進學解》：")
        self.assertEqual(
            [
                e.model_dump(exclude_defaults=True)
                for e in base_data.etymology_examples
            ],
            [
                {
                    "ref": "813年，韓愈《進學解》",
                    "tags": [
                        "Pinyin",
                        "Classical Chinese",
                        "Traditional Chinese",
                    ],
                    "text": "焚膏油以繼晷，恆兀兀以窮年。",
                    "bold_text_offsets": [
                        (0, 1),
                        (4, 5),
                    ],  # broken partial b tag
                    "roman": "Fén gāoyóu yǐ jì guǐ, héng wùwù yǐ qióng nián.",
                    "bold_roman_offsets": [(0, 7), (14, 20)],
                    "translation": "燃燒燈油夜以繼日，終年孜孜不倦刻苦用功。",
                },
                {
                    "ref": "813年，韓愈《進學解》",
                    "tags": [
                        "Pinyin",
                        "Classical Chinese",
                        "Simplified Chinese",
                    ],
                    "text": "焚膏油以继晷，恒兀兀以穷年。",
                    "bold_text_offsets": [(0, 1), (4, 5)],
                    "roman": "Fén gāoyóu yǐ jì guǐ, héng wùwù yǐ qióng nián.",
                    "bold_roman_offsets": [(0, 7), (14, 20)],
                    "translation": "燃燒燈油夜以繼日，終年孜孜不倦刻苦用功。",
                },
            ],
        )

    def test_etymology_sections(self):
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<div class="vsSwitcher" data-toggle-category="usage examples" style="border-left: 1px solid #930; border-left-width: 2px; padding-left: 0.8em;"><dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[隹#漢語|隹]][[珷#漢語|珷]][[王#漢語|王]][[既#漢語|既]][[克#漢語|克]][[大邑商#漢語|大邑商]]，[[𠟭#漢語|𠟭]][[廷#漢語|廷]][[吿#漢語|吿]][[于#漢語|于]][[天#漢語|天]]，[[曰#漢語|曰]]：[[余#漢語|余]][[𠀠#漢語|𠀠]][[宅#漢語|宅]][[𢆶#漢語|𢆶]]<b>𠁩</b><b>或</b>，[[自#漢語|自]][[之#漢語|之]][[辥#漢語|辥]][[民#漢語|民]]。<!-- -->}-</span><span class="vsHide"> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:上古漢語|早期上古漢語]]，[[w:繁体中文|繁體]]&#93;</span></span><span class="vsToggleElement" style="color:darkgreen; font-size:x-small;padding-left:10px"></span><hr><span class="vsHide"><span lang="zh-Hans" class="Hans">-{<!-- -->[[隹#漢語|隹]][[珷#漢語|珷]][[王#漢語|王]][[既#漢語|既]][[克#漢語|克]][[大邑商#漢語|大邑商]]，[[𠟭#漢語|𠟭]][[廷#漢語|廷]][[告#漢語|告]][[于#漢語|于]][[天#漢語|天]]，[[曰#漢語|曰]]：[[余#漢語|余]][[𠀠#漢語|𠀠]][[宅#漢語|宅]][[𢆶#漢語|𢆶]]<b>𠁩</b><b>或</b>，[[自#漢語|自]][[之#漢語|之]][[辥#漢語|辥]][[民#漢語|民]]。<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:上古漢語|早期上古漢語]]，[[w:简体中文|簡體]]&#93;</span></span><dd><span class="vsHide"><small>出自：[[:s:何尊銘文|何尊銘文]]</small></span></dd><dd><span class="vsHide"><span lang="zh-Latn" style="color:#404D52"><i>Wéi Wǔwáng jì kè Dàyìshāng, cè tíng gào yú Tiān, yuē: yú qí zhái zī <b>Zhōng</b><b>guó</b>, zì zhī yì mín.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></span></dd><dd>武王克商後告祭於天，說：「余入住天下中心，治理民眾。」</dd></dl>[[Category:有引文的文言文詞]]</div>""",
        )
        self.wxr.wtp.add_page(
            "Template:obor",
            10,
            """[[Appendix:Glossary#形譯詞|形譯詞]]自<span class="etyl">[[w:日语|日語]][[Category:源自日語的漢語借詞|丨03囗08]]</span> """,
        )
        page_data = parse_page(
            self.wxr,
            "中國",
            """==漢語==
===詞源1===
最早出現於西周青銅器何尊的銘文。參見中國的稱號。
{{zh-x|隹{wéi} ^珷-王 既 克 ^大邑商，𠟭{cè} 廷 吿{gào} 于 ^天，曰：余 𠀠{qí} 宅 𢆶{zī} ^'''@𠁩'''{zhōng}'''@或'''{guó}，自 之 辥{yì} 民。|武王克商後告祭於天，說：「余入住天下中心，治理民眾。」|CL-PC|ref=[[:s:何尊銘文|何尊銘文]]|collapsed=y}}
====專有名詞====
# 位於東亞的國家，首都為北京
====名詞====
# [[朝廷]]

===詞源2===
{{obor|zh|ja|-}}
====專有名詞====
# {{zh-div|地方|地區}} 日本中國地區，本州西部地區""",
        )
        self.assertEqual(
            page_data[0]["etymology_text"],
            "最早出現於西周青銅器何尊的銘文。參見中國的稱號。",
        )
        self.assertEqual(
            page_data[0]["etymology_text"], page_data[1]["etymology_text"]
        )
        self.assertEqual(page_data[0]["categories"], ["有引文的文言文詞"])
        self.assertEqual(page_data[0]["categories"], page_data[1]["categories"])
        self.assertEqual(len(page_data[0]["etymology_examples"]), 2)
        self.assertEqual(
            page_data[0]["etymology_examples"],
            page_data[1]["etymology_examples"],
        )
        self.assertEqual(page_data[2]["etymology_text"], "形譯詞自日語")
        self.assertEqual(page_data[2]["categories"], ["源自日語的漢語借詞"])
        self.assertTrue("etymology_examples" not in page_data[2])
