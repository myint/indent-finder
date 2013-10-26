check:
	pep8 indent_finder.py
	pylint \
		--rcfile=/dev/null \
		--reports=no \
		--disable=invalid-name \
		--disable=missing-docstring \
		--disable=too-few-public-methods \
		--disable=too-many-branches \
		--disable=too-many-return-statements \
		indent_finder.py
	rst2html --strict README.rst > /dev/null
	scspell indent_finder.py README.rst

coverage:
	@rm -f .coverage
	@coverage run --parallel-mode run_tests.py
	@coverage run --parallel-mode \
		indent_finder.py indent_finder.py Makefile missing_file
	@coverage run --parallel-mode \
		indent_finder.py --vim-output indent_finder.py && echo
	@coverage combine
	@coverage report
	@coverage html
	@rm -f .coverage
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

readme:
	@restview --strict README.rst


test:
	python2.4 run_tests.py
	python2.5 run_tests.py
	python2.6 run_tests.py
	python2.7 run_tests.py
	python3.2 run_tests.py
	python3.3 run_tests.py
