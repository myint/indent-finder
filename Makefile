check:
	pep8 indent_finder.py
	pep257 indent_finder.py
	pylint --reports=no --include-ids=yes --max-module-lines=2500 \
		--disable=C0111,C0103,E1123,F0401,R0902,R0903,W0232,W0404,W0622,R0914,R0912,R0915,R0904,R0911,R0913,W0142,E1101,E0702 \
		--rcfile=/dev/null indent_finder.py
	rst2html --strict README.rst > /dev/null
	scspell indent_finder.py README.rst

coverage:
	@rm -f .coverage
	@coverage run run_tests.py
	@coverage report
	@coverage html
	@rm -f .coverage
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

readme:
	@restview --strict README.rst
