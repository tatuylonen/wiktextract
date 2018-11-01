#!/bin/sh
set -e

echo "Remember to update version number in setup.py!"
echo "Press enter to continue"
read x

rm -rf dist build

python3 setup.py sdist bdist_wheel
#twine upload --repository-url https://test.pypi.org/legacy/ dist/*
twine upload dist/*
