import unittest
import collections
import wiktextract
from wiktextract.clean import clean_value, clean_quals
from wiktextract import WiktionaryConfig


class WiktExtractTests(unittest.TestCase):

    config = WiktionaryConfig()

    def test_pos(self):
        poses = wiktextract.PARTS_OF_SPEECH
        assert isinstance(poses, set)
        assert "noun" in poses
        assert "verb" in poses
        assert "pron" in poses
        assert "adj" in poses
        assert "adv" in poses
        assert "num" in poses
        assert len(poses) < 50

    def test_cv_plain(self):
        v = "This is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_comment(self):
        v = "This <!--comment--> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_repl0(self):
        v = "This is 1500 {{BC}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is 1500 BC")

    def test_cv_repl1(self):
        v = "This is a {{given name|en|female}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_arg1(self):
        v = "This is a {{given name|en|lang=fi|female}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_arg2(self):
        v = "This is a {{given name|en|female|lang=fi}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_surname(self):
        v = "This is a {{surname|from=nickname|lang=fi}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a surname")

    def test_cv_repl1_taxon(self):
        v = "{{taxon|genus|family|Talpidae|[[insectivore]] mammals; typical [[mole]]s}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, "taxonomic genus")

    def test_cv_arg1(self):
        v = "This is a {{w|test}}."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg2(self):
        v = "This is a {{w|test article|test value}}."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test value.")

    def test_cv_arg3(self):
        v = "This is a {{w2|fi||test}}."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg_nest(self):
        v = "This is a {{w2|fi||{{given name|en|male}}}}."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a male given name.")

    def test_cv_unk(self):
        v = "This is a {{unknown-asdxfa}} test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_ref(self):
        v = "This <ref>junk\nmore junk</ref> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html(self):
        v = "This <thispurportstobeatag> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html2(self):
        v = "This </thispurportstobeatag> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link1(self):
        v = "This is a [[test]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link2(self):
        v = "This is a [[w:foo|test]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_htmllink(self):
        v = "This is a [http://ylonen.org test]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q2(self):
        v = "This is a ''test''."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q3(self):
        v = "This is a '''test'''."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_nbsp(self):
        v = "This is a&nbsp;test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_gt(self):
        v = "This is a &lt;test&gt;."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a <test>.")

    def test_cv_gt(self):
        v = "This is a t\u2019est."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a t'est.")

    def test_cv_sp(self):
        v = "  This\nis \na\n   test.\t"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_presp(self):
        v = " This : is a test . "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This: is a test.")

    def test_cv_presp(self):
        v = " This ; is a test , "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This; is a test,")

    def test_cv_excl(self):
        v = " Run !\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run!")

    def test_cv_ques(self):
        v = " Run ?\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run?")

    def test_cv_nested1(self):
        v = "{{acronym of|es|{{w|Geroa Bai|lang=es}}}}"
        v = clean_value(self.config, v)
        self.assertEqual(v, 'acronym of "Geroa Bai"')

    def test_page1(self):
        v = """
{{lb|en|agriculture|and|soil science|of pasture soils}} Tending toward [[scouring#Noun|scouring]] (diarrheal illness) in [[graze#Verb|grazing]] livestock, being high in [[molybdenum]] content and neutral to alkaline in [[pH]].
 {{quote-journal |en|url=https://www.cabdirect.org/cabdirect/abstract/19412200374 |last=Green |first=H.H. |year=1940 |title=[Abstract of a forthcoming bulletin from {{w|Imperial Chemical Industries}}] |journal=[https://www.cabi.org/publishing-products/online-information-resources/veterinary-bulletin/ Veterinary Bulletin] |passage=Abstract: The novelty of the subject matter and the fact that the information is conveyed in the form of a bulletin addressed to farmers, pending later publication of further experimental data in the scientific press, justifies a lengthy abstract for readers of the ''Veterinary Bulletin''. The local word "'''teart'''" (i.e. [[tart]]) is applied to land and pastures [in {{w|Somerset}}, {{w|Warwickshire}}, and {{w|Gloucestershire}}] upon which severe scouring occurs in grazing [[ruminant]]s, particularly cows [[lactating|in milk]] and young stock. Sheep are less affected, and horses and pigs appear to be unaffected. […] Most affected farms contain both '''teart''' and non-teart land and the degree of "[[teartness]]" varies with season and from field to field. […] The cause of [[teartness]] is traced to the presence of molybdenum in the herbage in amounts varying from 20-100 [[ppm|p.p.m.]] of the dry matter, and the degree of [[teartness]] is roughly proportional to the molybdenum content, particularly to the amount in water-soluble form. Of the total molybdenum present, about 80% is soluble in the case of green grass, about 40% in the case of hay, and 10% in the case of moribund winter herbage. Hence growing [[pasture]]s may be '''teart''' even when cut [[hay]] is not. […] [Various [[ameliorant]]s are available but] Wherever possible, however, it is advisable to convert '''teart''' pastures to [[arable]] land. [H.H. Green, [[abstracter]], in an abstract of a forthcoming bulletin from {{w|Imperial Chemical Industries}}.<ref name="oclc_41934659">{{cite-book |oclc=41934659 |year=1941 |author=Ferguson WS |author2=Lewis AH |author3=Watson SJ |editors= |title=The Teart Pasture of Somerset: Cause of Teartness and its Prevention. Bulletin No. 1 of the {{w|Jealott's Hill#Syngenta research site|Jealott's Hill Research Station}}.}}</ref>]}}
 {{quote-journal |en|doi=10.1017/S0021859600048371 |last=Lewis |first=AH |year=1943 |title=The '''teart''' pastures of Somerset: II. Relation between soil and teartness |journal={{w|The Journal of Agricultural Science}} |volume=33 |issue=1 |pages=52-57 |passage='''Teart''' soils contain {{w|molybdenum}} in amounts varying from about 0·002 to 0·010% in the {{w|soil horizon#A horizon|surface horizon}} and are [[neutral]] or [[alkaline]] in reaction and often [[calcareous]]. The contents of molybdenum increase down the soil profile. Those [soils] which are acid in reaction in the surface horizons are not '''teart''' even if their molybdenum content is high. […] How a knowledge of the relation between soil and [[teartness]] can be turned to practical advantage is briefly discussed.}}"""
        v = clean_value(self.config, v)
        self.assertEqual(v, "(agriculture and soil science of pasture soils) Tending toward scouring (diarrheal illness) in grazing livestock, being high in molybdenum content and neutral to alkaline in pH.")

# XXX tests for clean_quals
