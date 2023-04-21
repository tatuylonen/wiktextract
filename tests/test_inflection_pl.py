# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.inflection import parse_inflection_section

class InflTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.wxr = WiktextractContext(WiktionaryConfig(), Wtp())
        
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        self.wxr.wtp.start_subsection(pos)
        tree = self.wxr.wtp.parse(text)
        data = {}
        parse_inflection_section(self.wxr, data, word, lang, pos,
                                 section, tree)
        return data

    def test_Polish_verb1(self):
        ret = self.xinfl("mówić", "Polish", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead+inflection-table-verb">Conjugation of <i class="Latn+mention" lang="pl">mówić</i>&nbsp;<span class="gender"><abbr title="imperfective+aspect">impf</abbr></span></div>
<div class="NavContent">

{| class="wikitable+inflection-table" style="margin%3A+1em+auto%3B"

|-

! rowspan="2" | &nbsp;


! &nbsp;


! colspan="3" title="liczba+pojedyncza" | singular


! colspan="2" title="liczba+mnoga" | plural


|-

! title="osoba" | person


! title="rodzaj+m%C4%99ski" | masculine


! title="rodzaj+%C5%BCe%C5%84ski" | feminine


! title="rodzaj+nijaki" | neuter


! title="rodzaj+m%C4%99skoosobowy" | virile


! title="rodzaj+niem%C4%99skoosobowy" | nonvirile


|-

! colspan="2" title="bezokolicznik" | infinitive


| colspan="5" | mówić


|-

! rowspan="4" title="czas+tera%C5%BAniejszy" | present tense


! title="pierwsza+osoba+%28ja%2C+my%29" | 1st


| colspan="3" | <span class="Latn" lang="pl">[[mówię#Polish|mówię]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[mówimy#Polish|mówimy]]</span>


|-

! title="druga+osoba+%28ty%2C+wy%29" | 2nd


| colspan="3" | <span class="Latn" lang="pl">[[mówisz#Polish|mówisz]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[mówicie#Polish|mówicie]]</span>


|-

! title="trzecia+osoba+%28on%2C+ona%2C+ono%2C+pan%2C+pani%2C+oni%2C+one%2C+pa%C5%84stwo%29" | 3rd


| colspan="3" | <span class="Latn" lang="pl">[[mówi#Polish|mówi]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[mówią#Polish|mówią]]</span>


|-

! title="forma+bezosobowa" | impersonal


| colspan="5" | <span class="Latn" lang="pl">[[mówi#Polish|mówi]] [[się#Polish|się]]</span>


|-

! rowspan="4" title="czas+przesz%C5%82y" | past tense


! title="pierwsza+osoba+%28ja%2C+my%29" | 1st


| <span class="Latn" lang="pl">[[mówiłem#Polish|mówiłem]]</span>


| <span class="Latn" lang="pl">[[mówiłam#Polish|mówiłam]]</span>


|


| <span class="Latn" lang="pl">[[mówiliśmy#Polish|mówiliśmy]]</span>


| <span class="Latn" lang="pl">[[mówiłyśmy#Polish|mówiłyśmy]]</span>


|-

! title="druga+osoba+%28ty%2C+wy%29" | 2nd


| <span class="Latn" lang="pl">[[mówiłeś#Polish|mówiłeś]]</span>


| <span class="Latn" lang="pl">[[mówiłaś#Polish|mówiłaś]]</span>


|


| <span class="Latn" lang="pl">[[mówiliście#Polish|mówiliście]]</span>


| <span class="Latn" lang="pl">[[mówiłyście#Polish|mówiłyście]]</span>


|-

! title="trzecia+osoba+%28on%2C+ona%2C+ono%2C+pan%2C+pani%2C+oni%2C+one%2C+pa%C5%84stwo%29" | 3rd


| <span class="Latn" lang="pl">[[mówił#Polish|mówił]]</span>


| <span class="Latn" lang="pl">[[mówiła#Polish|mówiła]]</span>


| <span class="Latn" lang="pl">[[mówiło#Polish|mówiło]]</span>


| <span class="Latn" lang="pl">[[mówili#Polish|mówili]]</span>


| <span class="Latn" lang="pl">[[mówiły#Polish|mówiły]]</span>


|-

! title="forma+bezosobowa" | impersonal


| colspan="5" | <span class="Latn" lang="pl">[[mówiono#Polish|mówiono]]</span>


|-

! rowspan="4" title="czas+przysz%C5%82y" | future tense


! title="pierwsza+osoba+%28ja%2C+my%29" | 1st


| <span class="Latn" lang="pl">[[będę#Polish|będę]] [[mówił#Polish|mówił]]</span>,<br>będę mówić<br>


| <span class="Latn" lang="pl">[[będę#Polish|będę]] [[mówiła#Polish|mówiła]]</span>,<br>będę mówić<br>


|


| <span class="Latn" lang="pl">[[będziemy#Polish|będziemy]] [[mówili#Polish|mówili]]</span>,<br>będziemy mówić<br>


| <span class="Latn" lang="pl">[[będziemy#Polish|będziemy]] [[mówiły#Polish|mówiły]]</span>,<br>będziemy mówić<br>


|-

! title="druga+osoba+%28ty%2C+wy%29" | 2nd


| <span class="Latn" lang="pl">[[będziesz#Polish|będziesz]] [[mówił#Polish|mówił]]</span>,<br>będziesz mówić<br>


| <span class="Latn" lang="pl">[[będziesz#Polish|będziesz]] [[mówiła#Polish|mówiła]]</span>,<br>będziesz mówić<br>


|


| <span class="Latn" lang="pl">[[będziecie#Polish|będziecie]] [[mówili#Polish|mówili]]</span>,<br>będziecie mówić<br>


| <span class="Latn" lang="pl">[[będziecie#Polish|będziecie]] [[mówiły#Polish|mówiły]]</span>,<br>będziecie mówić<br>


|-

! title="trzecia+osoba+%28on%2C+ona%2C+ono%2C+pan%2C+pani%2C+oni%2C+one%2C+pa%C5%84stwo%29" | 3rd


| <span class="Latn" lang="pl">[[będzie#Polish|będzie]] [[mówił#Polish|mówił]]</span>,<br>będzie mówić<br>


| <span class="Latn" lang="pl">[[będzie#Polish|będzie]] [[mówiła#Polish|mówiła]]</span>,<br>będzie mówić<br>


| <span class="Latn" lang="pl">[[będzie#Polish|będzie]] [[mówiło#Polish|mówiło]]</span>,<br>będzie mówić<br>


| <span class="Latn" lang="pl">[[będą#Polish|będą]] [[mówili#Polish|mówili]]</span>,<br>będą mówić<br>


| <span class="Latn" lang="pl">[[będą#Polish|będą]] [[mówiły#Polish|mówiły]]</span>,<br>będą mówić<br>


|-

! title="forma+bezosobowa" | impersonal


| colspan="5" | <span class="Latn" lang="pl">[[będzie#Polish|będzie]] mówić [[się#Polish|się]]</span>


|-

! rowspan="4" title="tryb+przypuszczaj%C4%85cy" | conditional


! title="pierwsza+osoba+%28ja%2C+my%29" | 1st


| <span class="Latn" lang="pl">[[mówiłbym#Polish|mówiłbym]]</span>


| <span class="Latn" lang="pl">[[mówiłabym#Polish|mówiłabym]]</span>


|


| <span class="Latn" lang="pl">[[mówilibyśmy#Polish|mówilibyśmy]]</span>


| <span class="Latn" lang="pl">[[mówiłybyśmy#Polish|mówiłybyśmy]]</span>


|-

! title="druga+osoba+%28ty%2C+wy%29" | 2nd


| <span class="Latn" lang="pl">[[mówiłbyś#Polish|mówiłbyś]]</span>


| <span class="Latn" lang="pl">[[mówiłabyś#Polish|mówiłabyś]]</span>


|


| <span class="Latn" lang="pl">[[mówilibyście#Polish|mówilibyście]]</span>


| <span class="Latn" lang="pl">[[mówiłybyście#Polish|mówiłybyście]]</span>


|-

! title="trzecia+osoba+%28on%2C+ona%2C+ono%2C+pan%2C+pani%2C+oni%2C+one%2C+pa%C5%84stwo%29" | 3rd


| <span class="Latn" lang="pl">[[mówiłby#Polish|mówiłby]]</span>


| <span class="Latn" lang="pl">[[mówiłaby#Polish|mówiłaby]]</span>


| <span class="Latn" lang="pl">[[mówiłoby#Polish|mówiłoby]]</span>


| <span class="Latn" lang="pl">[[mówiliby#Polish|mówiliby]]</span>


| <span class="Latn" lang="pl">[[mówiłyby#Polish|mówiłyby]]</span>


|-

! title="forma+bezosobowa" | impersonal


| colspan="5" | <span class="Latn" lang="pl">[[mówiono#Polish|mówiono]] [[by#Polish|by]]</span>


|-

! rowspan="3" title="tryb+rozkazuj%C4%85cy" | imperative


! title="pierwsza+osoba+%28ja%2C+my%29" | 1st


| colspan="3" | <span class="Latn" lang="pl">[[niech#Polish|niech]] [[mówię#Polish|mówię]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[mówmy#Polish|mówmy]]</span>


|-

! title="druga+osoba+%28ty%2C+wy%29" | 2nd


| colspan="3" | <span class="Latn" lang="pl">[[mów#Polish|mów]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[mówcie#Polish|mówcie]]</span>


|-

! title="trzecia+osoba+%28on%2C+ona%2C+ono%2C+pan%2C+pani%2C+oni%2C+one%2C+pa%C5%84stwo%29" | 3rd


| colspan="3" | <span class="Latn" lang="pl">[[niech#Polish|niech]] [[mówi#Polish|mówi]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[niech#Polish|niech]] [[mówią#Polish|mówią]]</span>


|-

! colspan="2" title="imies%C5%82%C3%B3w+przymiotnikowy+czynny" | active adjectival participle


| <span class="Latn" lang="pl">[[mówiący#Polish|mówiący]]</span>


| <span class="Latn" lang="pl">[[mówiąca#Polish|mówiąca]]</span>


| <span class="Latn" lang="pl">[[mówiące#Polish|mówiące]]</span>


| <span class="Latn" lang="pl">[[mówiący#Polish|mówiący]]</span>


| <span class="Latn" lang="pl">[[mówiące#Polish|mówiące]]</span>


|-

! colspan="2" title="imies%C5%82%C3%B3w+przymiotnikowy+bierny" | passive adjectival participle


| <span class="Latn" lang="pl">[[mówiony#Polish|mówiony]]</span>


| <span class="Latn" lang="pl">[[mówiona#Polish|mówiona]]</span>


| <span class="Latn" lang="pl">[[mówione#Polish|mówione]]</span>


| <span class="Latn" lang="pl">[[mówieni#Polish|mówieni]]</span>


| <span class="Latn" lang="pl">[[mówione#Polish|mówione]]</span>


|-

! colspan="2" title="imies%C5%82%C3%B3w+przys%C5%82%C3%B3wkowy+wsp%C3%B3%C5%82czesny" | contemporary adverbial participle


| colspan="5" | <span class="Latn" lang="pl">[[mówiąc#Polish|mówiąc]]</span>


|-

! colspan="2" title="rzeczownik+odczasownikowy" | verbal noun


| colspan="5" | <span class="Latn" lang="pl">[[mówienie#Polish|mówienie]]</span>


|-

|}
</div></div>
""")
        expected = {
            "forms": [
              {
                  "form": "imperfective",
                  "source": "Conjugation",
                  "tags": [
                      "table-tags"
                  ]
              },
              {
                "form": "mówić",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "mówię",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "mówimy",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "mówisz",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówicie",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "mówi",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówią",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "mówi się",
                "source": "Conjugation",
                "tags": [
                  "impersonal",
                  "present"
                ]
              },
              {
                "form": "mówiłem",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "masculine",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "mówiłam",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "mówiliśmy",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "mówiłyśmy",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "nonvirile",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "mówiłeś",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówiłaś",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówiliście",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "second-person",
                  "virile"
                ]
              },
              {
                "form": "mówiłyście",
                "source": "Conjugation",
                "tags": [
                  "nonvirile",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "mówił",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówiła",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówiło",
                "source": "Conjugation",
                "tags": [
                  "neuter",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówili",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "third-person",
                  "virile"
                ]
              },
              {
                "form": "mówiły",
                "source": "Conjugation",
                "tags": [
                  "nonvirile",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "mówiono",
                "source": "Conjugation",
                "tags": [
                  "impersonal",
                  "past"
                ]
              },
              {
                "form": "będę mówił",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "będę mówić",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "będę mówiła",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "future",
                  "singular"
                ]
              },
              {
                "form": "będę mówić",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "future",
                  "singular"
                ]
              },
              {
                "form": "będziemy mówili",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "będziemy mówić",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "będziemy mówiły",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "nonvirile",
                  "plural"
                ]
              },
              {
                "form": "będziemy mówić",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "nonvirile",
                  "plural"
                ]
              },
              {
                "form": "będziesz mówił",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "masculine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "będziesz mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "masculine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "będziesz mówiła",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "future",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "będziesz mówić",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "future",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "będziecie mówili",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "second-person",
                  "virile"
                ]
              },
              {
                "form": "będziecie mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "second-person",
                  "virile"
                ]
              },
              {
                "form": "będziecie mówiły",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "nonvirile",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "będziecie mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "nonvirile",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "będzie mówił",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "masculine",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "masculine",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówiła",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "future",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówić",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "future",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówiło",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "neuter",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "neuter",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "będą mówili",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "third-person",
                  "virile"
                ]
              },
              {
                "form": "będą mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "third-person",
                  "virile"
                ]
              },
              {
                "form": "będą mówiły",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "nonvirile",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "będą mówić",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "nonvirile",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "będzie mówić się",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "impersonal"
                ]
              },
              {
                "form": "mówiłbym",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "mówiłabym",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "feminine",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "mówilibyśmy",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "mówiłybyśmy",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "nonvirile",
                  "plural"
                ]
              },
              {
                "form": "mówiłbyś",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "masculine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówiłabyś",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "feminine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówilibyście",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person",
                  "virile"
                ]
              },
              {
                "form": "mówiłybyście",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "nonvirile",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "mówiłby",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "masculine",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówiłaby",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "feminine",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówiłoby",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "neuter",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "mówiliby",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person",
                  "virile"
                ]
              },
              {
                "form": "mówiłyby",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "nonvirile",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "mówiono by",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "impersonal"
                ]
              },
              {
                "form": "niech mówię",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "singular"
                ]
              },
              {
                "form": "mówmy",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "mów",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "mówcie",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "niech mówi",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "niech mówią",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "mówiący",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "masculine",
                  "participle",
                  "singular"
                ]
              },
              {
                "form": "mówiąca",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "feminine",
                  "participle",
                  "singular"
                ]
              },
              {
                "form": "mówiące",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "neuter",
                  "participle",
                  "singular"
                ]
              },
              {
                "form": "mówiący",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "participle",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "mówiące",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "nonvirile",
                  "participle",
                  "plural"
                ]
              },
              {
                "form": "mówiony",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "masculine",
                  "participle",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "mówiona",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "feminine",
                  "participle",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "mówione",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "neuter",
                  "participle",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "mówieni",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "participle",
                  "passive",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "mówione",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "nonvirile",
                  "participle",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "mówiąc",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "contemporary",
                  "participle"
                ]
              },
              {
                "form": "mówienie",
                "source": "Conjugation",
                "tags": [
                  "noun-from-verb",
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Polish_noun1(self):
        ret = self.xinfl("dziecko", "Polish", "noun", "Declension", """
<div class="NavFrame+inflection-table-noun" style="width%3A+29em">
<div class="NavHead">Declension of <span class="Latn mention" lang="pl" xml:lang="pl">dziecko</span></div>
<div class="NavContent">

{| style="width%3A+29em%3B+margin%3A+0%3B" class="wikitable+inflection-table"

|-

! style="width%3A+8em%3B" |


! scope="col" | singular


! scope="col" | plural


|-

! title="mianownik+%28kto%3F+co%3F%29" scope="row" | nominative


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecko]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieci#Polish|dzieci]]</span>


|-

! title="dope%C5%82niacz+%28kogo%3F+czego%3F%29" scope="row" | genitive


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecka#Polish|dziecka]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieci#Polish|dzieci]]</span>


|-

! title="celownik+%28komu%3F+czemu%3F%29" scope="row" | dative


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecku#Polish|dziecku]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieciom#Polish|dzieciom]]</span>


|-

! title="biernik+%28kogo%3F+co%3F%29" scope="row" | accusative


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecko]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieci#Polish|dzieci]]</span>


|-

! title="narz%C4%99dnik+%28kim%3F+czym%3F%29" scope="row" | instrumental


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieckiem#Polish|dzieckiem]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dziećmi#Polish|dziećmi]]</span>


|-

! title="miejscownik+%28o+kim%3F+o+czym%3F%29" scope="row" | locative


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecku#Polish|dziecku]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieciach#Polish|dzieciach]]</span>


|-

! title="wo%C5%82acz+%28o%21%29" scope="row" | vocative


| <span class="Latn" lang="pl" xml:lang="pl">[[dziecko]]</span>


| <span class="Latn" lang="pl" xml:lang="pl">[[dzieci#Polish|dzieci]]</span>


|}
</div></div>
""")
        expected = {
            "forms": [
              {
                  "form": "",
                  "source": "Declension",
                  "tags": [
                      "table-tags"
                  ]
              },
              {
                "form": "dziecko",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "dzieci",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "dziecka",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "dzieci",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "dziecku",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "dzieciom",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "dziecko",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "dzieci",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "dzieckiem",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "dziećmi",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "dziecku",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "dzieciach",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "dziecko",
                "source": "Declension",
                "tags": [
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "dzieci",
                "source": "Declension",
                "tags": [
                  "plural",
                  "vocative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Polish_adj1(self):
        ret = self.xinfl("wysoki", "Polish", "adj", "Declension", """
<div class="NavFrame+inflection-table-adj" style="width%3A+61em">
<div class="NavHead" align="left">declension of <i class="Latn mention" lang="pl" xml:lang="pl">wysoki</i></div>
<div class="NavContent">

{| class="wikitable+inflection-table" style="width%3A+61em%3B+margin%3A+0%3B+border%3A+none%3B"

|-

! rowspan="2" style="width%3A+11em%3B" title="przypadek" | case


! colspan="4" scope="colgroup" title="liczba+pojedyncza" | singular


! colspan="3" scope="colgroup" title="liczba+mnoga" | plural


|-

! style="min-width%3A+8em%3B" scope="col" title="rodzaj+m%C4%99skoosobowy%2Fm%C4%99skozwierz%C4%99cy" | masculine personal/animate


! style="min-width%3A+8em%3B" scope="col" title="rodzaj+m%C4%99skorzeczowy" | masculine inanimate


! style="min-width%3A+8em%3B" scope="col" title="rodzaj+nijaki" | neuter


! style="min-width%3A+8em%3B" scope="col" title="rodzaj+%C5%BCe%C5%84ski" | feminine


! style="min-width%3A+8em%3B" scope="col" title="rodzaj+m%C4%99skoosobowy" | virile


! style="min-width%3A+8em%3B" scope="col" title="rodzaj+niem%C4%99skoosobowy" | nonvirile


|-

! title="mianownik+%28jaki%3F+jaka%3F+jakie%3F%29%2C+wo%C5%82acz+%28o%21%29" scope="row" | nominative, vocative


| colspan="2" | <span class="Latn" lang="pl">[[wysoki#Polish|wysoki]]</span>


| <span class="Latn" lang="pl">[[wysokie#Polish|wysokie]]</span>


| <span class="Latn" lang="pl">[[wysoka#Polish|wysoka]]</span>


| <span class="Latn" lang="pl">[[wysocy#Polish|wysocy]]</span>


| <span class="Latn" lang="pl">[[wysokie#Polish|wysokie]]</span>


|-

! title="dope%C5%82niacz+%28jakiego%3F+jakiej%3F%29" scope="row" | genitive


| colspan="3" | <span class="Latn" lang="pl">[[wysokiego#Polish|wysokiego]]</span>


| rowspan="2" | <span class="Latn" lang="pl">[[wysokiej#Polish|wysokiej]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[wysokich#Polish|wysokich]]</span>


|-

! title="celownik+%28jakiemu%3F+jakiej%3F%29" scope="row" | dative


| colspan="3" | <span class="Latn" lang="pl">[[wysokiemu#Polish|wysokiemu]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[wysokim#Polish|wysokim]]</span>


|-

! title="biernik+%28jakiego%3F+jaki%3F+jak%C4%85%3F+jakie%3F%29" scope="row" | accusative


| <span class="Latn" lang="pl">[[wysokiego#Polish|wysokiego]]</span>


| <span class="Latn" lang="pl">[[wysoki#Polish|wysoki]]</span>


| <span class="Latn" lang="pl">[[wysokie#Polish|wysokie]]</span>


| rowspan="2" | <span class="Latn" lang="pl">[[wysoką#Polish|wysoką]]</span>


| <span class="Latn" lang="pl">[[wysokich#Polish|wysokich]]</span>


| <span class="Latn" lang="pl">[[wysokie#Polish|wysokie]]</span>


|-

! title="narz%C4%99dnik+%28jakim%3F+jak%C4%85%3F%29" scope="row" | instrumental


| colspan="3" rowspan="2" | <span class="Latn" lang="pl">[[wysokim#Polish|wysokim]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[wysokimi#Polish|wysokimi]]</span>


|-

! title="miejscownik+%28jakim%3F+jakiej%3F%29" scope="row" | locative


| <span class="Latn" lang="pl">[[wysokiej#Polish|wysokiej]]</span>


| colspan="2" | <span class="Latn" lang="pl">[[wysokich#Polish|wysokich]]</span>


|}

</div>
</div>
""")
        expected = {
            "forms": [
              {
                  "form": "",
                  "source": "Declension",
                  "tags": [
                      "table-tags"
                  ]
              },
              {
                "form": "wysoki",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "wysokie",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "wysoka",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "wysocy",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "virile",
                  "vocative"
                ]
              },
              {
                "form": "wysokie",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "nonvirile",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "wysokiego",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "wysokiej",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "wysokich",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "wysokiemu",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "wysokiej",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "wysokim",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "wysokiego",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "wysoki",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "inanimate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "wysokie",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "wysoką",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "wysokich",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "virile"
                ]
              },
              {
                "form": "wysokie",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "nonvirile",
                  "plural"
                ]
              },
              {
                "form": "wysokim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "wysoką",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "wysokimi",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "wysokim",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "wysokiej",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "wysokich",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)
