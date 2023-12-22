# Run "make test" to run tests
# Run "make clean" to remove automatically generated files
REPO ?= tatuylonen/wiktextract
SHA ?= HEAD

test:
	python -m unittest discover -b -s tests
test_coverage:
	python -m coverage erase
	python -m coverage run -m unittest discover -b -s tests
coverage_report:
	python -m coverage combine
	python -m coverage html
github_pages:
	python tools/generate_schema.py
	python tools/github_pages.py $(REPO) $(SHA)
clean:
	python -m coverage erase
	rm -rf __pycache__ _site
