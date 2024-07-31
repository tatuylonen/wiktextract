from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.example import extract_example_list_item
from wiktextract.extractor.ja.models import Example, Sense
from wiktextract.wxr_context import WiktextractContext


class TestJaExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ja"),
            WiktionaryConfig(
                dump_file_lang_code="ja",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_puppy(self):
        self.wxr.wtp.start_page("puppy")
        root = self.wxr.wtp.parse("""#* ''I have another two [[dozen]] of these '''puppies''' to [[finish]] before I can go home.''
#*:あと、2ダースも済まさないと帰れないよ。""")
        sense = Sense()
        extract_example_list_item(self.wxr, sense, root.children[0].children[0])
        self.assertEqual(
            sense.examples[0],
            Example(
                text="I have another two dozen of these puppies to finish before I can go home.",
                translation="あと、2ダースも済まさないと帰れないよ。",
            ),
        )

    def test_ref_before_text(self):
        self.wxr.wtp.start_page("料理")
        root = self.wxr.wtp.parse("""#*1955年、中谷宇吉郎「面白味」<ref>青空文庫（2013年1月4日作成）（底本：「中谷宇吉郎随筆集」岩波文庫、岩波書店、2011年1月6日第26刷）https://www.aozora.gr.jp/cards/001569/files/53235_49838.html</ref>
#*:それらを買って来て、いろいろな'''料理'''をしてくれたのであるが、そのうちの牛蒡の煮附には、ちょっと驚いた。""")
        sense = Sense()
        extract_example_list_item(self.wxr, sense, root.children[0].children[0])
        self.assertEqual(
            sense.examples[0],
            Example(
                text="それらを買って来て、いろいろな料理をしてくれたのであるが、そのうちの牛蒡の煮附には、ちょっと驚いた。",
                ref="1955年、中谷宇吉郎「面白味」 青空文庫（2013年1月4日作成）（底本：「中谷宇吉郎随筆集」岩波文庫、岩波書店、2011年1月6日第26刷）https://www.aozora.gr.jp/cards/001569/files/53235_49838.html",
            ),
        )

    def test_one_line(self):
        self.wxr.wtp.start_page("なきむし")
        self.wxr.wtp.add_page(
            "テンプレート:ふりがな",
            10,
            "<ruby>[[{{{1}}}]]<rp>（</rp><rt>[[{{{2}}}]]</rt><rp>）</rp></ruby>",
        )
        root = self.wxr.wtp.parse(
            "#* {{ふりがな|尤|もっと|も}}も僕は[[気の毒]]にも{{ふりがな|度|たびたび}}大島を[[なく|泣か]]せては、[[なきむし|泣虫]][[なきむし|泣虫]]と[[からかう|からかひ]]しものなり。 （[[w:芥川龍之介|芥川龍之介]]『学校友だち』）〔1925年〕"
        )
        sense = Sense()
        extract_example_list_item(self.wxr, sense, root.children[0].children[0])
        self.assertEqual(
            sense.examples[0],
            Example(
                text="尤も僕は気の毒にも度大島を泣かせては、泣虫泣虫とからかひしものなり。",
                ref="（芥川龍之介『学校友だち』）〔1925年〕",
                ruby=[("尤", "もっと"), ("度", "たびたび")],
            ),
        )
