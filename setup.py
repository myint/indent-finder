#!/usr/bin/env python

from distutils.core import setup

setup( 	name = "Indentation Finder",
		version = "1.2",
		description = "Finds of check the indentation used in programming source files",
		author = "Philippe Fremy",
		author_email = "phil at freehackers dot org",
		maintainer = "Philippe Fremy",
		maintainer_email = "phil at freehackers dot org",
		license = "BSD license",
		url="http://phil.freehackers.org/indent-finder/index.html",
		py_modules = [ "indent_finder", "indent_checker" ]
		)
