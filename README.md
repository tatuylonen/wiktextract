# Wiktextract

This is a utility and Python package for for extracing data from Wiktionary.

*2022-06-20: Version 1.99.7 is now on pypi and available for installation using
  pip (Python3).  Think of it as a beta version for 2.0.0.  There is
  also a new version of wikitextprocessor.*

Please report issues on github and I'll try to address them reasonably
soon.

The current extracted version is available for browsing and download
at: [https://kaikki.org/dictionary/](http://kaikki.org/dictionary/).
I plan to maintain an automatically updating version of the data at
this location.  For most people the preferred way to get the extracted
Wiktionary data will be to just take it from the web site.

Note: extracting all data for all languages from the English
Wiktionary may take from an hour to several days, depending
on your computer.  Expanding Lua modules is not cheap, but it enables
superior extraction quality and maintainability! You may want to look
at the pre-expanded downloads instead of running it yourself.

## Overview

This is a Python package and tool for extracting information from
English Wiktionary (enwiktionary) data dumps.  Note that the English
Wiktionary contains extensive dictionaries and inflectional
information for many languages, not just English.  Only its glosses
and internal tagging are in English.

One thing that distinguishes this tool from any system I'm aware of is
that this tool expands templates and Lua macros in Wiktionary.  That
enables much more accurate rendering and extraction of glosses, word
senses, inflected forms, and pronunciations.  It also makes the system
much easier to maintain.  All this results in much higher extraction
quality and accuracy.

This tool extracts glosses, parts-of-speech, declension/conjugation
information when available, translations for all languages when
available, pronunciations (including audio file links), qualifiers
including usage notes, word forms, links between words including
hypernyms, hyponyms, holonyms, meronyms, related words, derived terms,
compounds, alternative forms, etc.  Links to Wikipedia pages, Wikidata
identifiers, and other such data are also extracted when available.
For many classes of words, a word sense is annotated with specific
information such as what word it is a form of, what is the RGB value
of the color it represents, what is the numeric value of a number,
what SI unit it represents, etc.

This tool extracts information for all languages that have data in the
English wiktionary.  It also extracts translingual data and
information about characters (anything that has an entry in Wiktionary).

This tool reads the ``enwiktionary-<date>-pages-articles.xml.bz2``
dump file and outputs JSON-format dictionaries containing most of the
information in Wiktionary.  The dump files can be downloaded from
https://dumps.wikimedia.org.

This utility will be useful for many natural language processing,
semantic parsing, machine translation, and language generation
applications both in research and industry.

The tool can be used to extract machine translation dictionaries,
language understanding dictionaries, semantically annotated
dictionaries, and morphological dictionaries with
declension/conjugation information (where this information is
available for the target language).  Dozens of languages have
extensive vocabulary in ``enwiktionary``, and several thousand
languages have partial coverage.

The ``wiktwords`` script makes extracting the information for use by
other tools trivial without writing a single line of code.  It
extracts the information specified by command options for languages
specified on the command line, and writes the extracted data to a file
or standard output in JSON format for processing by other tools.

While there are currently no active plans to support parsing
non-English wiktionaries, I'm considering it.  Now that this builds on
[wikitextprocessor](https://github.com/tatuylonen/wikitextprocessor/)
and expands templates and Lua macros, it would be fairly
straightforward to build support for other languages too - and even
make the extraction configurable so that only a configuration file
would need to be created for processing a Wiktionary in a new
language.

As far as we know, this is the most comprehensive tool available for
extracting information from Wiktionary as of December 2020.

If you find this tool and/or the pre-extracted data helpful, please
give this a star on github!

## Pre-extracted data

For most people, it may be easiest to just download pre-expanded data.
Please see
[https://kaikki.org/dictionary/rawdata.html](https://kaikki.org/dictionary/rawdata.html).
The raw wiktextract data, extracted category tree, extracted templates
and modules, as well as a bulk download of audio files for
pronunciations in both <code>.ogg</code> and <code>.mp3</code> formats
are available.

There is a also download link at the bottom of every page and a button
to view the JSON produced for each page.  You can download all data,
data for a specific language, data just a single word, or data for a
list of related words (e.g., a particular part-of-speech or words
relating to a particular topic or having a particular inflectional
form).  All downloads are in [JSON Lines](https://jsonlines.org/) format (each line is a separate JSON
object).  The bigger downloads are also available in compressed form.

Some people have asked for the full data as a single JSON object
(instead of the current one JSON object per line format).  I've
decided to keep it as a JSON object per line, because loading all the
data into Python requires about 120 GB of memory.  It is much easier to
process the data line-by-line, especially if you are only interested
in a part of the information.  You can easily read the files using the
following code:

```python
import json

with open("filename.json", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        ... parse the data in this record
```

If you want to collect all the data into a list, you can read the file
into a list with:

```python
import json

lst = []
with open("filename.json", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        lst.append(data)
```

You can also easily pretty-print the data into a more human-readable form using:

```python
print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
```

Here is a pretty-printed example of an extracted word entry for the
word `thrill` as an English verb (only one part-of-speech is shown here):

```python
{
  "categories": [
    "Emotions"
  ],
  "derived": [
    {
      "word": "enthrill"
    }
  ],
  "forms": [
    {
      "form": "thrills",
      "tags": [
        "present",
        "simple",
        "singular",
        "third-person"
      ]
    },
    {
      "form": "thrilling",
      "tags": [
        "present"
      ]
    },
    {
      "form": "thrilled",
      "tags": [
        "participle",
        "past",
        "simple"
      ]
    }
  ],
  "head_templates": [
    {
      "args": {},
      "expansion": "thrill (third-person singular simple present thrills, present participle thrilling, simple past and past participle thrilled)",
      "name": "en-verb"
    }
  ],
  "lang": "English",
  "lang_code": "en",
  "pos": "verb",
  "senses": [
    {
      "glosses": [
        "To suddenly excite someone, or to give someone great pleasure; to electrify; to experience such a sensation."
      ],
      "tags": [
        "ergative",
        "figuratively"
      ]
    },
    {
      "glosses": [
        "To (cause something to) tremble or quiver."
      ],
      "tags": [
        "ergative"
      ]
    },
    {
      "glosses": [
        "To perforate by a pointed instrument; to bore; to transfix; to drill."
      ],
      "tags": [
        "obsolete"
      ]
    },
    {
      "glosses": [
        "To hurl; to throw; to cast."
      ],
      "tags": [
        "obsolete"
      ]
    }
  ],
  "sounds": [
    {
      "ipa": "/\u03b8\u0279\u026al/"
    },
    {
      "ipa": "[\u03b8\u027e\u032a\u030a\u026a\u026b]",
      "tags": [
        "UK",
        "US"
      ]
    },
    {
      "ipa": "[\u03b8\u027e\u032a\u030a\u026al]",
      "tags": [
        "Ireland"
      ]
    },
    {
      "ipa": "[t\u032a\u027e\u032a\u030a\u026al]",
      "tags": [
        "Ireland"
      ]
    },
    {
      "rhymes": "-\u026al"
    },
    {
      "audio": "en-us-thrill.ogg",
      "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/d/db/En-us-thrill.ogg/En-us-thrill.ogg.mp3",
      "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/d/db/En-us-thrill.ogg",
      "tags": [
        "US"
      ],
      "text": "Audio (US)"
    }
  ],
  "translations": [
    {
      "code": "nl",
      "lang": "Dutch",
      "sense": "suddenly excite someone, or to give someone great pleasure; to electrify",
      "word": "opwinden"
    },
    {
      "code": "fi",
      "lang": "Finnish",
      "sense": "suddenly excite someone, or to give someone great pleasure; to electrify",
      "word": "syk\u00e4hdytt\u00e4\u00e4"
    },
    {
      "code": "fi",
      "lang": "Finnish",
      "sense": "suddenly excite someone, or to give someone great pleasure; to electrify",
      "word": "riemastuttaa"
    },
...
    {
      "code": "tr",
      "lang": "Turkish",
      "sense": "slight quivering of the heart that accompanies a cardiac murmur",
      "word": "\u00e7arp\u0131nt\u0131"
    }
  ],
  "wikipedia": [
    "thrill"
  ],
  "word": "thrill"
}
```

## Getting started

### Installing

Preparation: on Linux (example from Ubuntu 20.04), you may need to
first install the `build-essential` and `python3-dev` packages
with `apt update && apt install build-essential python3-dev python3-pip lbzip2`.

Install `wiktextract` from source:

```
git clone https://github.com/tatuylonen/wiktextract.git
cd wiktextract
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install --use-pep517 .
```

Alternatively, you can install the package from pypi.org:

```
python -m pip install wiktextract
```

This software requires Python 3.

### Running tests

This package includes tests written using the `unittest` framework.
They can be run using, for example, `nose2`, which can be installed
using `python -m pip install --use-pep517 -e ".[dev]"`.

To run the tests, use the following command in the top-level directory:

```
make test
```

(Unfortunately the test suite for ``wiktextract`` is not yet very
comprehensive.  The underlying lower-level toolkit,
``wikitextprocessor``, has much more extensive test coverage.)

### Expected performance

Extracting all data for all languages from English Wiktionary takes
about 1.25 hours on a 128-core dual AMD EPYC 7702 system.  The
performance is expected to be approximately linear with the number of
processor cores, provided you have enough memory (about 10GB/core or
5GB/hyperthread recommended).

You can control the number of parallel processes to use with the
``--num-threads`` option; the default on Linux is to use the number of
available cores/hyperthreads.  On Windows and MacOS, ``--num-threads``
should currently be set to 1 (default on those systems). We don't
really recommend using Windows or Mac for the extraction, because it
will be very slow.  Extracting only a few languages or a subset of the data
will be faster.

You can download the full pre-extracted data from
[kaikki.org](https://kaikki.org/dictionary/). The pre-extraction is
updated regularly with the latest Wiktionary dump.  Using the
pre-extracted data may be the easiest option unless you have special
needs or want to modify the code.

### Installing and running tests on Windows with VS Code

Tested with Python 3.9.4.

- Create [a Python virtual environment](https://code.visualstudio.com/docs/python/environments#_creating-environments)
(venv) in the VS Code workspace with the cloned repo. It should automatically install the package.

- Open a new terminal. It should be PowerShell. You may need to [fix terminal permissions](https://stackoverflow.com/questions/56199111/visual-studio-code-cmd-error-cannot-be-loaded-because-running-scripts-is-disabl/67420296#67420296)
in order for it to pick up the virtual environment correclty.

- In the terminal run this command:

```
py -m nose2 -B
```

## Using the command-line tool

The ``wiktwords`` script is the easiest way to extract data from
Wiktionary.  Just download the data dump file from
[dumps.wikimedia.org](https://dumps.wikimedia.org/enwiktionary/) and
run the script.  The correct dump file the name
``enwiktionary-<date>-pages-articles.xml.bz2``.

An example of a typical invocation for extracting all data would be:
```
wiktwords --all --all-languages --out data.json enwiktionary-20201201-pages-articles.xml.bz2
```

If you wish to modify the code or test processing individual pages,
the following may also be useful:

1. Pass a path to save database file that you can use for quickly
processing individual pages:

```
wiktwords --db-path /tmp/wikt-db enwiktionary-20201201-pages-articles.xml.bz2
```

2. To process a single page and produce a human-readable output file
for debugging:

```
wiktwords --db-path /tmp/wikt-db --all --all-languages --out outfile --page page_title
```

The following command-line options can be used to control its operation:

* --out FILE: specifies the name of the file to write (specifying "-" as the file writes to stdout)
* --all-languages: extract words for all available languages
* --language LANGUAGE_CODE: extracts the given language (this option may be specified multiple times; by default, English [en] and Translingual [mul] words are extracted)
* --list-languages: prints a list of supported language names
* --dump-file-language-code LANGUAGE_CODE: specifies the language code for the Wiktionary edition that the dump file is for (defaults to "en"; "zh" is supported and others are being added)
* --all: causes all data to be captured for the selected languages
* --translations: causes translations to be captured
* --pronunciation: causes pronunciation information to be captured
* --linkages: causes linkages (synonyms etc.) to be captured
* --examples: causes usage examples to be captured
* --etymologies: causes etymology information to be captured
* --descendants: causes descendants information to be captured
* --inflections: causes inflection tables to be captured
* --redirects: causes redirects to be extracted
* --pages-dir DIR: save all wiktionary pages under this directory (mostly for debugging)
* --db-path PATH: save/use database from this path (for debugging)
* --page FILE or TITLE: read page from file or database, can be specified multiple times(first line must be "TITLE: pagetitle"; file should use UTF-8 encoding)
* --num-threads THREADS: use this many parallel processes (needs 4GB/process)
* --human-readable: print human-readable JSON with indentation (no longer
machine-readable)
* --override PATH: override pages with files in this directory(first line of the file must be TITLE: pagetitle)
* --templates-file: extract Template namespace to this tar file
* --modules-file: extract Module namespace to this tar file
* --categories-file: extract Wiktionary category tree into this file as JSON (see description below)
* --inflection_tables_file: extract and expand tables into this file as wikitext; use this to create tests
* --help: displays help text (with some more options than listed here)

## Calling the library

While this package has been mostly intended to be used using the
`wiktwords` command, it is also possible to call this as a library.
Underneath, this uses the `wikitextprocessor` module. For more usage
examples please read the [wiktwords.py](https://github.com/tatuylonen/wiktextract/blob/master/wiktextract/wiktwords.py) and [wiktionary.py](https://github.com/tatuylonen/wiktextract/blob/master/wiktextract/wiktionary.py) files.

This code can be called from an application as follows:

```python
from wiktextract import (
    WiktextractContext,
    WiktionaryConfig,
    parse_wiktionary,
)
from wikitextprocessor import Wtp

config = WiktionaryConfig(
    dump_file_lang_code="en",
    capture_language_codes=["en", "mul"],
    capture_translations=True,
    capture_pronunciation=True,
    capture_linkages=True,
    capture_compounds=True,
    capture_redirects=True,
    capture_examples=True,
    capture_etymologies=True,
    capture_descendants=True,
    capture_inflections=True
)
wxr = WiktextractContext(Wtp(), config)

def word_cb(data):
    # data is dictionary containing information for one word/redirect
    ... do something with data

RECOGNIZED_NAMESPACE_NAMES = [
    "Main",
    "Category",
    "Appendix",
    "Project",
    "Thesaurus",
    "Module",
    "Template",
    "Reconstruction"
]

namespace_ids = {
    wxr.wtp.NAMESPACE_DATA.get(name, {}).get("id")
    for name in RECOGNIZED_NAMESPACE_NAMES
}

parse_wiktionary(wxr, path, word_cb, False, False, namespace_ids)
```

The capture arguments default to ``True``, so they only need to be set if
some values are not to be captured (note that the ``wiktwords``
program sets them to ``False`` unless the ``--all`` or specific capture
options are used).

#### parse_wiktionary()

```python
def parse_wiktionary(
    wxr: Wiktextractcontext,
    path: str,
    word_cb,
    phase1_only: bool,
    dont_parse: bool,
    namespace_ids: Set[int],
    override_folders: Optional[List[str]] = None,
    skip_extract_dump: bool = False,
    save_pages_path: Optional[str] = None
):
```

The ``parse_wiktionary`` function will call ``word_cb(data)`` for
words and redirects found in the Wiktionary dump.  ``data`` is
information about a single word and part-of-speech as a dictionary and
may include several word senses.  It may also be a redirect (indicated
by the presence of a "redirect" key in the dictionary).  It is in the same
format as the JSON-formatted dictionaries returned by the
``wiktwords`` tool.

Its arguments are as follows:
* ``wxr`` (WiktextractContext) - a Wiktextract-level processing context
  containing fields that point to a Wtp context and WiktionarConfig object
  (below).
** ``wxr.wtp`` (Wtp) - a
  [wikitextprocessor](https://github.com/tatuylonen/wikitextprocessor/)
  processing context.  The number of parallel processes to use can be
  given as the ``num_threads`` argument to the constructor, and a database
  file path can be provided as the ``db_path`` argument.
** ``wxr.config`` (WiktionaryConfig) - a configuration object describing
  what to exctract (see below)
* ``path`` (str) - path to a Wiktionary dump file (*-pages-articles.xml.bz2)
* ``word_cb`` (function) - this function will be called for every word
  extracted from Wiktionary.  The argument is a dictionary.  Typically it
  will be called once for each word form and part-of-speech (each time there
  may be more than one word sense under "senses").  See below for a description
  of the dictionary.
* ``phase1_only`` - if this is set to ``True``, then only a cache file will
  be created but no extraction will take place.  In this case the ``Wtp``
  constructor should probably be given the ``db_path`` argument when
  creating ``wxr.wtp``.
* `namespace_ids` - a set of namespace ids, pages have namespace ids that not
  included in this set won't be processed. Avaliable id values can be
  found in wikitextprocessor project's [data/en/namespaces.json](https://github.com/tatuylonen/wikitextprocessor/blob/main/wikitextprocessor/data/en/namespaces.json)
  file and the Wiktionary *.xml.bz2 dump file.
* `override_folders` - override pages with files in these directories.
* `skip_extract_dump` - skip extract dump file if database exists.
* `save_pages_path` - path for storing extracted pages.

This call gathers statistics in ``wxr.config``.  This function will
automatically parallelize the extraction.  ``page_cb`` will be called in
the parent process, however.

#### parse_page()

```python
def parse_page(
    wxr: WiktextractContext, word: str, text: str
) -> List[Dict[str, str]]
```

This function parses ``text`` as if it was a Wiktionary page with the
title ``title``.  The arguments are:
* ``wxr`` (WiktextractContext) - a ``wiktextract`` context containing:
** ``wxr.wtp`` (Wtp) - a ``wikitextprocessor`` context
** ``wxr.config`` (WiktionaryConfig) - specifies what to capture and is also used
* ``title`` (str) - the title to use for the page
* ``text`` (str) - contents of the page (wikitext)
  for collecting statistics

#### PARTS_OF_SPEECH

This is a constant set of all part-of-speech values (``pos`` key) that
may occur in the extracted data.  Note that the list is somewhat larger than
what a conventional part-of-speech list would be.

### class WiktextractContext(object)

The ``WiktextractContext`` object is used to hold the ``wikitextprocessor``-
specific ``Wtp`` context object and the wiktextract's ``WiktionaryConfig``
objects, and XXX in the future it will hold actual context that doesn't
belong in Wtp and XXX WiktionaryConfig will be most probably integrated
into the WiktextractContext object proper.

The constructor is called simply by supplying a Wtp and WiktionaryConfig
object:

```python
# Blanks slate for testing, usually
wxr = WiktextractContext(Wtp(), WiktionaryConfig())
```

or

```python
# separately initialized config with a bunch of arguments like in the
# example in the -> class WiktionaryConfig(object)-section below
wxr = WiktextractContext(wtp, config)
```

if it is more conveneint
### class WiktionaryConfig(object)

The ``WiktionaryConfig`` object is used for specifying what data to collect
from Wiktionary and is also used for collecting statistics during
extraction. Currently, it is a field of the WiktextractContext context object.

The constructor is called as:

```python
WiktionaryConfig(dump_file_lang_code="en",
                 capture_language_codes=["en", "mul"],
                 capture_translations=True,
                 capture_pronunciation=True,
                 capture_linkages=True,
                 capture_compounds=True,
                 capture_redirects=True,
                 capture_examples=True,
                 capture_etymologies=True,
                 capture_descendants=True,
                 capture_inflections=True)
```

The arguments are as follows:
* ``capture_language_codes`` (list/tuple/set of strings) - codes of
  languages for which to capture data.  It defaults to ``["en",
  "mul"]``. To capture all languages, set it to `None`.
* ``capture_translations`` (boolean) - set to ``False`` to disable capturing
  translations.  Translation information seems to be most
  widely available for the English language, which has translations into
  other languages.
* ``capture_pronunciation`` (boolean) - set to ``False`` to disable
  capturing pronunciations.  Typically, pronunciations include
  IPA transcriptions and any audio files included in the word entries, along
  with other information (including dialectal tags).  The type and amount of
  pronunciation information varies widely between languages.
* ``capture_linkages`` (boolean) - set to ``False`` to disable capturing
  linkages between word, such as hypernyms, antonyms, synonyms, etc.
* ``capture_compounds`` (boolean) - set to ``False`` to disable capturing
  compound words containing the word.  Compound word capturing is not currently
  fully implemented.
* ``capture_redirects`` (boolean) - set to ``False`` to disable capturing
  redirects.  Redirects are not associated with any specific language
  and thus requesting them returns them for all words in all languages.
* ``capture_examples`` (boolean) - set to ``False`` to disable
  capturing usage examples.
* ``capture_etymologies`` (boolean) - set to ``False`` to
  disable capturing etymologies.
* ``capture_descendants`` (boolean) - set to ``False`` to
  disable capturing descendants.
* ``capture_inflections`` (boolean) - set to ``False`` to
  disable capturing inflection tables.

## Format of extracted redirects

Some pages in Wiktionary are redirects.  For these, ``word_cb`` will
be called with data in a special format.  In this case, the dictionary
will have a ``redirect`` key, which will contain the page title that
the entry redirects to.  The ``title`` key contains the word/term that
contains the redirect.  Redirect entries do not have ``pos`` or any of
the other fields.  Redirects also are not associated with any
language, so all redirects are always returned regardless of the
captured languages (if extracting redirects has been requested).

## Format of the extracted word entries

Information returned for each word is a dictionary.  The dictionary has the
following keys (others may also be present or added later):

* ``word`` - the word form
* ``pos`` - part-of-speech, such as "noun", "verb", "adj", "adv", "pron", "determiner", "prep" (preposition), "postp" (postposition), and many others.  The complete list of possible values returned by the package can be found in ``wiktextract.PARTS_OF_SPEECH``.
* ``lang`` - name of the language this word belongs to (e.g., ``English``)
* ``lang_code`` - Wiktionary language code corresponding to ``lang`` key (e.g., ``en``)
* ``senses`` - list of word senses (dictionaries) for this word/part-of-speech (see below)
* ``forms`` - list of inflected or alternative forms specified for the word (e.g., plural, comparative, superlative, roman script version).  This is a list of dictionaries, where each dictionary has a ``form`` key and a ``tags`` key.  The ``tags`` identify what type of form it is.  It may also contain "ipa", "roman", and "source" fields.  The form can be "-" when the word is marked as not having that form (some of those will be word-specific, while others are language-specific; post-processing can drop such forms when no word has a value for that tag combination).
* ``sounds`` - list of dictionaries containing pronunciation, hyphenation, rhyming, and related information.  Each dictionary may have a ``tags`` key containing tags that clarify what kind of form that entry is.  Different types of information are stored in different fields: ``ipa`` is [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) pronunciation, ``enPR`` is [enPR](https://en.wikipedia.org/wiki/Pronunciation_respelling_for_English) pronunciation, ``audio`` is name of sound file in Wikimedia commons.
* ``categories`` - list of non-disambiguated categories for the word
* ``topics`` - list of non-disambiguated topics for the word
* ``translations`` - non-disambiguated translation entries (see below)
* ``etymology_text`` - etymology section as cleaned text
* ``etymology_templates`` - templates and their arguments and expansions from
  the etymology section.  These can be used to easily parse etymological
  relations.  Certain common templates that do not signify etymological
  relations are not included.
* ``etymology_number`` - for words with multiple numbered etymologies, this contains the number of the etymology under which this entry appeared
* ``descendants`` - descendants of the word (see below)
* ``synonyms`` - non-disambiguated synonym linkages for the word (see below)
* ``antonyms`` - non-disambiguated antonym linkages for the word (see below)
* ``hypernyms`` - non-disambiguated hypernym linkages for the word (see below)
* ``holonyms`` - non-disambiguated linkages indicating being part of something (see below) (not systematically encoded)
* ``meronyms`` - non-disambiguated linkages indicating having a part (see below) (fairly rare)
* ``derived`` - non-disambiguated derived word linkages for the word (see below)
* ``related`` - non-disambiguated related word linkages for the word (see below)
* ``coordinate_terms`` - non-disambiguated coordinate term linkages for the word (see below)
* ``wikidata`` - non-disambiguated Wikidata identifer
* ``wiktionary`` - non-disambiguated page title in Wikipedia (possibly prefixed by language id)
* ``head_templates``: part-of-speech specific head tags for the word.  This basically just captures the templates (their name and arguments) as a list of dictionaries.  Most applications may want to ignore this.
* ``inflection_templates`` - conjugation and declension templates found for the word, as dictionaries.  These basically capture the language-specific inflection template for the word.  Note that for some languages inflection information is also contained in ``head_templates``.  XXX in the very near future, we will start parsing inflections from the inflection tables into ``forms``, so there is usually no need to use the ``inflection_templates`` data.

There may also be other fields.

Note that several of the field on the word entry level indicate
information that has not been sense-disambiguated.  Such information
may apply to one or more of the senses.  Currently only the most
trivial cases are disambiguated; however, it is anticipated that more
disambiguation may be performed in the future.  It is also possible
for the same key to be provided in a sense and in the word entry; in
that case, the data in the sense has been sense-disambiguated and the
data in the word entry has not (and may not be apply to any particular
sense, regardless of whether the sense has some related
sense-disambiguated information).

### Word senses

Each word entry may have multiple glosses under the ``senses`` key.  Each
sense is a dictionary that may contain the following keys (among others, and more may be added in the future):

* ``glosses`` - list of gloss strings for the word sense (usually only one).  This has been cleaned, and should be straightforward text with no tagging.
* ``raw_glosses`` - list of gloss strings for the word sense, with less cleaning than ``glosses``.  In particular, parenthesized parts that have been parsed from the gloss into ``tags`` and ``topics`` are still present here.  This version may be easier for humans to interpret.
* ``tags`` - list of qualifiers and tags for the gloss.  This is a list of strings, and may include words such as "archaic", "colloquial", "present", "participle", "plural", "feminine", and many others (new words may appear arbitrarily).
* ``categories`` - list of sense-disambiguated category names extracted from (a subset) of the Category links on the page
* ``topics`` - list of sense-disambiguated topic names (kind of similar to categories but determined differently)
* ``alt_of`` - list of words that his sense is an alternative form of; this is a list of dictionaries, with field ``word`` containing the linked word and optionally ``extra`` containing additional text
* ``form_of`` - list of words that this sense is an inflected form of; this is a list of dictionaries, with field ``word`` containing the linked word and optionally ``extra`` containing additional text
* ``translations`` - sense-disambiguated translation entries (see below)
* ``synonyms`` - sense-disambiguated synonym linkages for the word (see below)
* ``antonyms`` - sense-disambiguated antonym linkages for the word (see below)
* ``hypernyms`` - sense-disambiguated hypernym linkages for the word (see below)
* ``holonyms`` - sense-disambiguated linkages indicating being part of something (see below) (not systematically encoded)
* ``meronyms`` - sense-disambiguated linkages indicating having a part (see below) (fairly rare)
* ``coordianate_terms`` - sense-disambiguated coordinate_terms linkages (see below)
* ``derived`` - sense-disambiguated derived word linkages for the word (see below)
* ``related`` - sense-disambiguated related word linkages for the word (see below)
* ``senseid`` - list of textual identifiers collected for the sense.  If there is a QID for the entry (e.g., Q123), those are stored in the ``wikidata`` field.
* ``wikidata`` - list of QIDs (e.g., Q123) for the sense
* ``wikipedia`` - list of Wikipedia page titles (with optional language code prefix)
* ``examples`` - list of usage examples, each example being a dictionary with ``text`` field containing the example text, optional ``ref`` field containing a source reference, optional ``english`` field containing English translation, optional ``type`` field containing example type (currently ``example`` or ``quotation`` if present), optional ``roman`` field containing romanization (for some languages written in non-Latin scripts), and optional (rare) ``note`` field contains English-language parenthesized note from the beginning of a non-english example.
* ``english`` - if the word sense has a qualifier that could not be parsed, that qualifier is put in this field (rare).  Most qualifiers parsed into ``tags`` and/or ``topics``.  The gloss with the qualifier still present can be found in ``raw_glosses``.

### Pronunciation

Pronunciation information is stored under the ``sounds`` key.  It is a
list of dictionaries, each of which may contain the following keys,
among others:

* ``ipa`` - pronunciation specifications as an IPA string /.../ or [...]
* ``enpr`` - pronunciation in English pronunciation respelling
* ``audio`` - name of a sound file in WikiMedia Commons
* ``ogg_url`` - URL for an OGG Vorbis format sound file
* ``mp3_url`` - URL for an MP3 format sound file
* ``audio-ipa`` - IPA string associated with the audio file, generally giving IPA transcription of what is in the sound file
* ``homophones`` - list of homophones for the word
* ``hyphenation`` - list of hyphenations
* ``tags`` - other labels or context information attached to the pronunciation entry (e.g., might indicate regional variant or dialect)
* ``text`` - text associated with an audio file (often not very useful)

Note that Wiktionary audio files are available for bulk download at
[https://kaikki.org/dictionary/rawdata.html](https://kaikki.org/dictionary/rawdata.html).
Files in the download are named with the last component of the URL in
``ogg_url`` and/or ``mp3_url``.  Downloading them individually takes
serveral days and puts unnecessary load on Wikimedia servers.

### Translations

Translations are stored under the ``translations`` key in the word's
data (if not sense-disambiguated) or in the word sense (if
sense-disambiguated).  They are stored in a list of dictionaries,
where each dictionary has the following keys (and possibly others):

* ``alt`` - optional alternative form of the translation (e.g., in a different script)
* ``code`` - Wiktionary's 2 or 3-letter language code for the language the translation is for
* ``english`` - English text, generally clarifying the target sense of the translation
* ``lang``  the language name that the translation is for
* ``note`` - optional text describing or commenting on the translation
* ``roman`` - optional romanization of the translation (when in non-Latin characters)
* ``sense`` - optional sense indicating the meaning for which this is a translation (this is a free-text string, and may not match any gloss exactly)
* ``tags`` - optional list of qualifiers for the translations, e.g., gender
* ``taxonomic`` - optional taxonomic name of an organism mentioned in the translation
* ``word`` - the translation in the specified language (may be missing when ``note`` is present)

### Etymologies

Etymological information is stored under the ``etymology_text`` and
``etymology_templates`` keys in the word's data.  When multiple parts-of-speech
are listed under the same etymology, the same data is copied to each
part-of-speech entry under that etymology.

The ``etymology_text`` field contains the contents of the whole etymology
section cleaned into human-readable text (i.e., templates have been expanded
and HTML tags removed, among other things).

The ``etymology_templates`` field contains a list of templates from
the etymology section.  Some common templates considered not relevant
for etymological information have been removed (e.g., ``redlink
category`` and ``isValidPageName``).  The list also includes nested
templates referenced from templates directly used in the etymology
description.  Each template in the list is a dictionary with the following
keys:
* ``name`` - name of the template
* ``args`` - dictionary mapping argument names to their cleaned values.  Positional arguments have keys that are numeric strings, starting with "1".
* ``expansion`` - the (cleaned) text the template expands to.

### Descendants

If a word has a "Descendants" section, the `descendants` key will appear in the word's data. It contains a list of objects corresponding to each line in the section, where each object has the following keys:

* `depth`: The level of indentation of the current line. This can be used to track the hierarchical structure of the list.
* `templates`: An array of objects corresponding to templates that appear on the line. The structure of each of these objects is the same as the structure of each object in `etymology_templates`.
* `text`: The expanded and cleaned line text, akin to `etymology_text`.

`descendants` data will also appear for the special case of "Derived terms" and "Extensions" sections for words that are roots in reconstructed languages, as these sections have the same format.

### Linkages to other words

Linkages (``synonyms``, ``antonyms``, ``hypernyms``, ``derived
words``, ``holonyms``, ``meronyms``, ``derived``, ``related``,
``coordinate_terms``) are stored in the word's data if not
sense-disambiguated, and in the word sense if sense-disambiguated.
They are lists of dictionaries, where each dictionary can contain the
following keys, among others:

* ``alt`` - optional alternative form of the target (e.g., in a different script)
* ``english`` - optional English text associated with the sense, usually identifying the linked target sense
* ``roman`` - optional romanization of a linked word in a non-Latin script
* ``sense`` - text identifying the word sense or context (e.g., ``"to rain very heavily"``)
* ``tags``: qualifiers specified for the sense (e.g., field of study, region, dialect, style)
* ``taxonomic``: optional taxonomic name associated with the linkage
* ``topics``: list of topic descriptors for the linkage (e.g., ``military``)
* ``word`` - the word this links to (string)

## Category tree data format

The ``--categories-file`` option extracts the Wiktionary category tree
as JSON into the specified file.  The data is extracted from the Wiktionary
Lua modules by evaluating them.

The data written to the JSON file is a dictionary, with the top-level
keys ``roots`` and ``nodes``.

Roots is a list of top-level nodes that are not children of other
nodes.  ``Fundamental`` is the normal top-level node; other roots may
reflect errors in the hierarchy in Wiktionary.  While not a root, the
category ``all topics`` contains the subhierarchy of topical
categories (e.g., ``food and drink``, ``nature``, ``sciences``, etc.).

Nodes is a dictionary mapping lowercased category name to a dictionary
containing data about the category.  For each category, the following
fields may be present:

* ``name`` (always present): non-lowercased name of the category (note, however,
  that many categories are originally lowercase in the Wiktionary
  hierarchy)
* ``desc``: optional description of the category
* ``clean_desc``: optional cleaned description of the category, with wikitext formatting cleaned to human-readable text, except {{{langname}}} (and possibly other similar tags) are left intact.
* ``children``: optional list of child categories of the category
* ``sort``: optional list of sorts (types of subcategories?).

The categories are returned as they are in the original Wiktionary
category data.  Language-specific categories are generally not
included.  However, there is a category ``{{{langcat}}}`` that appears
to contain a lot of the categories that have language-specific
variants.  Also, the category tree data does not contain language
prefixes (the tree is defined in Wiktionary without prefixes and then
replicated for each language).

## Related packages

The
[wikitextprocessor](https://github.com/tatuylonen/wikitextprocessor)
is a generic module for extracting data from Wiktionary, Wikipedia, and
other WikiMedia dump files.  ``wiktextract`` is built using this module.

*When using a version of wiktextract from github, please also setup
wikitextprocessor so that they have rough parity. The pypi versions of these
packages are usually out-of-date, and mixing a newer version with an older
one will lead to bugs. These packages are being developed in parallel.*

The [wiktfinnish](https://github.com/tatuylonen/wiktfinnish) package
can be used to interpret Finnish noun declinations and verb
conjugations and for generating Finnish inflected word forms.

## Publications

If you use Wiktextract or the extracted data in academic work, please
cite the following article:

Tatu Ylonen: [Wiktextract: Wiktionary as Machine-Readable Structured
data](http://www.lrec-conf.org/proceedings/lrec2022/pdf/2022.lrec-1.140.pdf),
Proceedings of the 13th Conference on Language Resources and
Evaluation (LREC), pp. 1317-1325, Marseille, 20-25 June 2022.

Linking to [https://kaikki.org](https://kaikki.org) or the relevant
sub-pages would also be greatly appreciated.

## Related tools

A few other tools also exist for parsing Wiktionaries.  These include
[Dbnary](http://kaiko.getalp.org/about-dbnary/),
[Wikiparse](https://github.com/frankier/wikiparse), and [DKPro
JWKTL](https://dkpro.github.io/dkpro-jwktl/).

## Contributing and reporting bugs

Please report bugs and other issues on github.  I also welcome
suggestions for improvement.

Please email to ``ylo`` at ``clausal.com`` if you wish to contribute
or have patches or suggestions.

## License

Copyright (c) 2018-2020 [Tatu Ylonen](https://ylonen.org).  This
package is free for both commercial and non-commercial use.  It is
licensed under the MIT license.  See the file
[LICENSE](https://github.com/tatuylonen/wiktextract/blob/master/LICENSE)
for details.  (Certain files have different open source licenses)
