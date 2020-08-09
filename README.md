# Wiktextract

This is a utility and Python package for for extracing data from Wiktionary.

**Currently working on this, and the repository may be broken on some
  days.  New release with major changes expected in August 2020.  This has
  gotten significantly delayed, and I apologize, but now I finally really
  should be able to work on this in August.**

## Overview

This is a Python package and tool for extracting information from
English Wiktionary (enwiktionary) data dumps.  Note that the English
Wiktionary contains extensive dictionaries and inflectional
information for many languages, not just English.  Only its glosses
and internal tagging are in English.

This tool reads the ``enwiktionary-<date>-pages-articles.xml.bz2``
file and outputs JSON-format dictionaries containing most of the
information in Wiktionary.

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

The tool is capable of extracting information for any language.
However, so far it has mostly been tested with English and Finnish,
and to some extent German and Spanish.  Changes to extract information
for any additional languages are likely to be small.  Basic
information extraction most likely works out of the box for any
language, but you may need to tweak the code to extract inflection or
pronunciation information for other languages.

There are currently no plans to support reading non-English
wiktionaries, even though many other languages can also be extracted
from ``enwiktionary``.  Adding support for other Wiktionaries would
require extensive work and maintenance, as each Wiktionary uses a
different tagging scheme.  Again, the English Wiktionary contains a
good coverage of many languages.

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

As far as we know, this is the most comprehensive tool available for
extracting information from Wiktionary as of November 2018.

## Getting started

### Installing

To install ``wiktextract``, use ``pip`` (or ``pip3``, as appropriate),
or clone the repository and install from the source:

```
git clone https://github.com/tatuylonen/wiktextract.git
cd wiktextract
python3 setup.py install
```

This will install the ``wiktextract`` package and the ``wiktwords`` script.

Note that this software has currently only been tested with Python 3.
Back-porting to Python 2.7 should not be difficult; it just hasn't been
tested yet.  Please report back if you test and make this work with
Python 2.

### Running tests

This package includes tests written using the ``unittest`` framework.
They can be run using, for example, ``nose``, which can be installed
using ``pip3 install nose``.

To run the tests, just use the following command in the top-level directory:
```
nosetests
```

## Using the command-line tool

The ``wiktwords`` script is the easiest way to extract data from
Wiktionary.  Just download the data dump file from
[dumps.wikimedia.org](https://dumps.wikimedia.org/enwiktionary/) and
run the script.  The correct dump file the name
``enwiktionary-<date>-pages-articles.xml.bz2``.

The command-line tool may be invoced as follows:

```
wiktwords data/enwiktionary-latest-pages-articles.xml.bz2 --out wikt.words --language English --all
```

The following command-line options are supported:

* --out FILE: specifies the name of the file to write (specifying "-" as the file writes to stdout)
* --language LANGUAGE: extracts the given language (this option may be specified multiple times; by default, English and Translingual words are extracted)
* --list-languages: prints a list of supported language names
* --all-languages: extract words for all available languages
* --all: causes all data to be captured for the selected languages
* --translations: causes translations to be captured
* --pronunciation: causes pronunciation information to be captured
* --linkages: causes linkages (hypernyms etc.) to be captured
* --compounds: causes compound words using each word to be captured
* --redirects: causes redirects to be extracted
* --statistics: prints useful statistics at the end
* --pages-dir DIR: save all wiktionary pages under this directory (mostly for debugging)
* --help: displays help text

Extracting all of English Wiktionary may take about an hour, depending
on the speed of your system.

## Calling the library

The library can be called as follows:

```
from wiktextract import (WiktionaryConfig, parse_wiktionary,
                         wiktionary_languages, PARTS_OF_SPEECH)

config = WiktionaryConfig(
             capture_languages=["English", "Translingual"],
             capture_translations=True,
             capture_pronunciation=True,
             capture_linkages=True,
             capture_compounds=True,
             capture_redirects=True)
parse_wiktionary(path, config, word_cb, capture_cb)
```

The ``parse_wiktionary`` call will call ``word_cb(data)`` for words
and redirects found in the Wiktionary dump.  ``data`` is information
about a single word and part-of-speech as a dictionary (multiple
senses of the same part-of-speech are combined into the same
dictionary).  It may also be a redirect (indicated by presence of a
"redirect" key in the dictionray).  It is in the same format as the
JSON-formatted dictionaries returned by the ``wiktwords`` tool.  The
format is described below.

``capture_cb(title, text)`` is called for every page before extracting any
words from it.  It should return True if the page should be analyzed, and
False if the page should be ignored.  It can also be used to write certain
pages to disk or capture certain pages for different analyses (e.g., extracting
hierarchies, classes, thesauri, or topic-specific word lists).  If this
callback is None, all pages are analyzed.

``capture_languages`` should be a list, tuple, or set of language names to
capture.  It defaults to ``["English", "Translingual"]``.

``capture_translations`` can be set to True to capture translation
information for words.  Translation information seems to be most
widely available for the English language, which has translations into
other languages.  The translation information increases the size and
loading time of the captured data substantially, so this is disabled
by default.

``capture_pronunciations`` should be set to True to capture pronunciation
information for words.  Typically, this includes IPA transcriptions
and any audio files included in the word entries, along with other
information.  However, the type and amount of pronunciation
information varies widely between languages.  This is disabled by
default since many applications won't need the information.

``capture_linkages`` should be set to True to capture linkages between
word, such as hypernyms, antonyms, synonyms, etc.

``capture_compounds`` should be set to True to capture compound words
containing the word.

``capture_redirects`` should be set to True to capture redirects.  Redirects
are not associated with any specific language and thus requesting them
returns them for words in all languages.

## Format of extracted redirects

Some pages in Wiktionary are redirects.  For these, ``word_cb`` will
be called with data in a special format.  In this case, the dictionary
will have the key ``redirect``, which will contain the name of the
word the entry redirects to.  The key ``word`` contains the word/term
that contains the redirect.  Redirect entries do not have ``pos`` or
any of the other fields.  Redirects also are not associated with any
language, so all redirects are always returned regardless of the captured
languages (if extracting redirects has been requested).

## Format of the extracted word entries

Information returned for each word is a dictionary.  The dictionary has the
following keys (others may also be present or added later):

* ``word``: the word form
* pos: part-of-speech, such as "noun", "verb", "adj", "adv", "pron", "determiner", "prep" (preposition), "postp" (postposition), and many others.  The complete list of possibel values returned by the package can be found in ``wiktextract.PARTS_OF_SPEECH``.
* ``senses``: word senses for this word/part-of-speech (see below)
* ``conjugation``: conjugation and declension entries found for the word, as dictionaries
* ``heads``: part-of-speech specific head tags for the word.  Useful for, e.g., obtaining comparatives, superlatives, and other inflection information for many languages.  Each value is a dictionary, basically containing the arguments of the corresponding template in Wiktionary, with the template name under "template_name".
* ``hyphenation``: list of hyphenations for the word when available.  Each hyphenation is a sequence of syllables.
* ``pinyin``: for Chinese words, the romanized transliteration, when available
* ``synonyms``: synonym linkages for the word (see below)
* ``antonyms``: antonym linkages for the word (see below)
* ``hypernyms``: hypernym linkages for the word (see below)
* ``holonyms``: linkages indicating being part of something (see below) (not systematically encoded)
* ``meronyms``: linkages indicating having a part (see below) (fairly rare)
* ``derived``: derived word linkages for the word (see below)
* ``related``: related word linkages for the word (see below)
* ``pronunciations``: contains pronunciation information when collected (see below)
* ``translations``: contains translation information when collected (see below)

XXX update this, there are now some additional fields and some format changes

### Word senses

Each part-of-speech may have multiple glosses under the ``senses`` key.  Each
sense is a dictionary that may contain the following keys (among others, and more may be added in the future):

* ``glosses``: list of gloss strings for the word sense (usually only one).  This has been cleaned, and should be straightforward text with no tagging.
* ``nonglosses``: list of gloss-like strings but that are not traditional glossary entries describing the word's meaning
* ``tags``: list of qualifiers and tags for the gloss.  This is a list of strings, and may include words such as "archaic", "colloquial", "present", "plural", "person", "organism", "british", "chemistry", "given name", "surname", "female", and many othes (new words may appear arbitrarily).  Some effort has been put into trying to canonicalize various sources and styles of annotation into a consistent set of tags, but it is impossible to do an exact job at this.
* ``senseid``: list of identifiers collected for the sense.  Some entries have a Wikidata identifier (Q<numbers>) here; others may have other identifiers.  Currently sense ids are not very widely annotated in Wiktionary.
* ``wikipedia``: link to wikipedia page from the word sense/gloss
* ``topics``: topic categories specified for the sense (these may also be in "tags")
* ``taxon``: links to taxonomical data
* ``categories``: Category links specified for the page
* ``color``: specification of RGB color values (hex or CSS color name)
* ``value``: value represented by the word (e.g., for numerals)
* ``unit``: information about units of measurement, particularly SI units, tagged to the word
* ``alt_of``: list of words of which this sense is an alternative form or abbreviation
* ``inflection_of``: list of words that this sense is an inflection of
* ``conjugation``: list of templates indicating conjugation/declension (list of dictionaries containing the arguments of the Wiktionary template, with template name under "template_name")

### Linkages to other words

Linkages (``synonyms``, ``antonyms``, ``hypernyms``, ``derived words``, ``holonyms``, ``meronyms``, ``derived``, ``related``) are lists of dictionaries, where each dictionary can contain the following keys, among others:

* ``word``: the word this links to (string).  If this starts with "Thesaurus:", then this entry is a link to a thesaurus page in Wiktionary.  If this starts with "Category:", then this refers to a category page in Wiktionary.
* ``sense``: text identifying the word sense or context.  This may also be a title from a table where the links are shown (e.g., "Derived terms of name that are not hyponyms").
* ``tags``: qualifiers specified for the sense (e.g., field of study, region, dialect, style).  This is a list of strings.

### Pronunciation

Pronunciation information is stored under the ``pronunciations`` key.  It is a
list of dictionaries, each of which may contain the following keys,
among others:

* ``audios``: list of audio files referenced as a list of ``(languagecode, filename, description)``
* ``ipa``: pronunciation specifications as IPA strings
* ``special_ipa``: special IPA-like specifications (sometimes macros calling code in Wiktionary), as list of dictionaries
* ``enpr``: pronunciations in English pronunciation format as list of strings
* ``homophones``: list of homophones for the word
* ``accent``: accent markers associated with the pronunciation specification, such as dialect, country, etc.  Common values for English include, e.g., "RP" (for Received Pronunciation), "US", "UK", "GA" (General American), etc.  A list (in the form of code) can be found [here](https://en.wiktionary.org/wiki/Module:accent_qualifier/data).
* ``tags``: other labels or context information attached to the sense (free form)
* ``sense``: optional sense specifier, e.g., "noun", "verb", "anatomy sense" (a string)

### Translations

Translations, when captured, are stored under the ``translations`` key
in the word's data.  They are stored in a list of dictionaries, where
each dictionary has the following keys (and possibly others):

* ``lang``: the language that the translation is for (Wiktionary's 2 or 3-letter language code)
* ``word``: the translation in the specified language
* ``sense``: optional sense for which the translation is (this is a free-text string, and may not match any gloss exactly)
* ``alt``: an optional alternative form of the translation (used when the translation is not a lemma form/page name; in those cases, ``word`` is the page name and ``alt`` contains the actual translated form)
* ``roman``: an optional romanization of the translation
* ``script``: optional name of the script that the translation is in
* ``tags``: optional list of [gender/number specifiers](https://en.wiktionary.org/wiki/Module:gender_and_number)

## Related packages

The [wiktfinnish](https://github.com/tatuylonen/wiktfinnish) package
can be used to interpret Finnish noun declications and verb
conjugations and for generating Finnish inflected word forms.

## Known issues

* Some information that is global for a page, such as category links for the page, may only be included in the last part-of-speech defined on the page or even the last language defined on the page.  This should be fixed.

This software is still quite new and should still be considered a beta
version.

## Dependencies

This package depends on the following other packages:

* [lxml](https://lxml.de)
* [wikitextparser](https://pypi.org/project/WikiTextParser/)

## Related tools

A few other tools also exist for parsing Wiktionaries.  These include
[Dbnary](http://kaiko.getalp.org/about-dbnary/),
[Wikiparse](https://github.com/frankier/wikiparse), and [DKPro
JWKTL](https://dkpro.github.io/dkpro-jwktl/).

## Contributing

The official repository of this project is on
[github](https://github.com/tatuylonen/wiktextract).

Please report bugs and other issues on github.

Please email to ylo at clausal.com if you wish to contribute or have
patches or suggestions.

## License

Copyright (c) 2018-2020 [Tatu Ylonen](https://ylonen.org).  This
package is free for both commercial and non-commercial use.  It is
licensed under the MIT license.  See the file
[LICENSE](https://github.com/tatuylonen/wiktextract/blob/master/LICENSE)
for details.

Credit and linking to the project's website and/or citing any future
papers on the project would be highly appreciated.
