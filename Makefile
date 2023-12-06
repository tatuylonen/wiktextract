# Run "make test" to run tests (with coverage analysis left in ./htmlcov)
# Run "make clean" to remove automatically generated files
test:
	python -m unittest discover -s tests
test_coverage:
	python -m coverage erase
	python -m coverage run -m unittest discover -s tests
coverage_report:
	python -m coverage combine
	python -m coverage html
clean:
	python -m coverage erase
	rm -rf __pycache__ htmlcov*
