# Run "make test" to run tests (with coverage analysis left in ./htmlcov)
# Run "make clean" to remove automatically generated files

test:
	rm -rf .coverage
	nose2 --output-buffer --with-coverage --coverage-report=html --coverage-config=testcov.conf --pretty-assert
	rm -rf htmlcov
	mv -f htmlcov.new htmlcov

clean:
	rm -rf __pycache__
	rm -rf .coverage htmlcov*
