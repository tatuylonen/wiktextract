# Run "make test" to run tests (with coverage analysis left in ./htmlcov)
# Run "make clean" to remove automatically generated files

test:
	rm -rf .coverage htmlcov
	python -m nose2 --output-buffer --pretty-assert --with-coverage --coverage-report=html
quicktest:
	python -m nose2 --output-buffer --pretty-assert
clean:
	rm -rf __pycache__
	rm -rf .coverage* htmlcov*
