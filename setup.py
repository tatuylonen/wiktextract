#!/usr/bin/env python3
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See LICENSE and https://ylonen.org

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="wiktextract",
      version="1.99.7",
      description="Wiktionary dump file parser and multilingual data extractor",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Tatu Ylonen",
      author_email="ylo@clausal.com",
      url="https://ylonen.org",
      license="MIT",
      download_url="https://github.com/tatuylonen/wiktextract",
      scripts=["wiktwords"],
      packages=["wiktextract"],
      include_package_data=True,
      install_requires=["wikitextprocessor", "python-Levenshtein", "nltk"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Text Processing",
          "Topic :: Text Processing :: Linguistic",
          ])
