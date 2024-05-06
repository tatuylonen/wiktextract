from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.etymology import extract_etymology
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestNote(TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(lang_code="zh"), Mock())

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_zh_x(self):
        self.wxr.wtp.start_page("一刻千金")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<div class="vsSwitcher" data-toggle-category="使用例" style="border-left: 1px solid #930; border-left-width: 2px; padding-left: 0.8em;"><dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[春宵#漢語|春宵]]<b>[[一刻#漢語|一刻]]</b>[[直#漢語|直]]<b>[[千金#漢語|千金]]</b>，[[花#漢語|花]][[有#漢語|有]][[清香#漢語|清香]][[月#漢語|月]][[有#漢語|有]][[陰#漢語|陰]]。<!-- -->}-</span><span class="vsHide"> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[繁體中文|繁體]]&#93;</span></span><span class="vsToggleElement" style="color:darkgreen; font-size:x-small;padding-left:10px"></span><hr><span class="vsHide"><span lang="zh-Hans" class="Hans">-{<!-- -->[[春宵#漢語|春宵]]<b>[[一刻#漢語|一刻]]</b>[[直#漢語|直]]<b>[[千金#漢語|千金]]</b>，[[花#漢語|花]][[有#漢語|有]][[清香#漢語|清香]][[月#漢語|月]][[有#漢語|有]][[阴#漢語|阴]]。<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[簡體中文|簡體]]&#93;</span></span><dd><span class="vsHide"><small>來自：宋．蘇軾《春夜》</small></span></dd><dd><span class="vsHide"><span lang="Latn" style="color:#404D52"><i>Chūnxiāo <b>yīkè</b> zhí <b>qiānjīn</b>, huā yǒu qīngxiāng yuè yǒu yīn.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></span></dd><dd>春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。</dd></dl>[[Category:有引文的文言文詞]]</div>""",
        )
        root = self.wxr.wtp.parse("""===詞源===
源自宋．[[w:蘇軾|蘇軾]]《春夜》詩：
{{zh-x|春宵 '''一刻''' 直 '''千金'''，花 有 清香 月 有 陰。|春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。|CL|ref=宋．蘇軾《春夜》|collapsed=y}}""")
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
                    "raw_tags": ["文言文", "繁體"],
                    "text": "春宵一刻直千金，花有清香月有陰。",
                    "roman": "Chūnxiāo yīkè zhí qiānjīn, huā yǒu qīngxiāng yuè yǒu yīn.",
                    "translation": "春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。",
                },
                {
                    "ref": "宋．蘇軾《春夜》",
                    "raw_tags": ["文言文", "簡體"],
                    "text": "春宵一刻直千金，花有清香月有阴。",
                    "roman": "Chūnxiāo yīkè zhí qiānjīn, huā yǒu qīngxiāng yuè yǒu yīn.",
                    "translation": "春天的夜晚非常寶貴，僅僅一刻卻值得千金價，花朵散發陣陣清香，月光投射出朦朧陰影。",
                },
            ],
        )
