#!/usr/bin/env python

from distutils.core import setup

import indent_finder



setup( 	name = "Indentation Finder",
		version = indent_finder.VERSION,
		description = "Finds of check the indentation used in programming source files",
		author = "Philippe Fremy",
		author_email = "phil at freehackers dot org",
		maintainer = "Philippe Fremy",
		maintainer_email = "phil at freehackers dot org",
		license = "BSD license",
		url="http://www.freehackers.org/Indent_Finder",
		py_modules = [ "indent_finder" ]
		)
