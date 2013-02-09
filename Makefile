check:
	pep8 indent_finder.py setup.py
	pep257 indent_finder.py setup.py
	pylint --report=no --include-ids=yes --disable=C0103,F0401,R0914,W0404,W0622 --rcfile=/dev/null indent_finder.py setup.py
	python setup.py --long-description | rst2html --strict > /dev/null
	scspell indent_finder.py setup.py README.rst

coverage:
	@rm -f .coverage
	@coverage run run_tests.py
	@coverage report
	@coverage html
	@rm -f .coverage
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

readme:
	@restview --long-description
