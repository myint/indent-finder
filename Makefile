check:
	pep8 indent_finder.py setup.py
	pep257 indent_finder.py setup.py
	pylint --reports=no --include-ids=yes --max-module-lines=2500 \
		--disable=C0111,C0103,E1123,F0401,R0902,R0903,W0404,W0622,R0914,R0912,R0915,R0904,R0911,R0913,W0142,E1101,E0702 \
		--rcfile=/dev/null indent_finder.py
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
