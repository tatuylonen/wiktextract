#!/usr/bin/env python3
#
# Copyright (c) 2018 Tatu Ylonen.  See LICENSE and https://ylonen.org

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="wiktextract",
      version="0.1.2",
      description="Wiktionary dump file parser and multilingual data extractor",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Tatu Ylonen",
      author_email="ylo@clausal.com",
      url="https://clausal.com",
      license="MIT",
      download_url="https://github.com/tatuylonen/wiktextract",
      scripts=["wiktwords"],
      packages=["wiktextract"],
      install_requires=["lxml", "wikitextparser"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Natural Language :: Finnish",
          "Operating System :: OS Independent",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Text Processing",
          "Topic :: Text Processing :: Linguistic",
          ])
