#!/usr/bin/env python3

from distutils.core import setup
setup(name="wiktextract",
      version="0.1",
      description="Wiktionary dump file parser and multilingual data extractor",
      author="Tatu Ylonen",
      author_email="ylo@clausal.com",
      url="https://clausal.com",
      license="MIT",
      download_url="https://github.com/tatuylonen/wiktextract",
      scripts=["wiktwords"],
      packages=["wiktextract"])
