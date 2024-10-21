# Extractor Template

This is an example / blank template for a Wiktextract subextractor. You can use
it as a jumping off point by copying this to a new folder in src/wiktextract/
extractor/, in a new directory with the name of the language-code / subdomain
of the Wiktionary you want to extract from. So, to make a Greek extractor, copy
this to src/wiktextract/extractor/el/ for el.wiktionary.org.

It is based on the Simple English extractor in src/wiktextract/extractor/simple,
which has more complete code, with a few changes and most of the SEW-specific
code removed. Both this template and the SEW have extensive (and sometimes
overlapping) comments.
