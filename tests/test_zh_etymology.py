from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.etymology import extract_etymology
from wiktextract.extractor.zh.models import WordEntry
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
        page_data = [base_data]
        extract_etymology(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[0].etymology_text, "源自宋．蘇軾《春夜》詩："
        )
        self.assertEqual(
            [
                e.model_dump(exclude_defaults=True)
                for e in page_data[0].etymology_examples
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
        page_data = [base_data]
        extract_etymology(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(page_data[0].etymology_text, "出自唐·韓愈《進學解》：")
        self.assertEqual(
            [
                e.model_dump(exclude_defaults=True)
                for e in page_data[0].etymology_examples
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
