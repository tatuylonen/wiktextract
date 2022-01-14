# Run "make test" to run tests (with coverage analysis left in ./htmlcov)
# Run "make clean" to remove automatically generated files

# --with-coverage --coverage-report=html --coverage-config=tests/testcov.conf
test:
	rm -rf .coverage*
	nose2 --output-buffer --pretty-assert
	# rm -rf htmlcov
	# mv -f htmlcov.new htmlcov

clean:
	rm -rf __pycache__
	rm -rf .coverage* htmlcov*
