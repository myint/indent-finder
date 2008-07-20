
Indentation finder, by Philippe Fremy <phil at freehackers dot org>
Copyright 2002-2008 Philippe Fremy

This program is distributed under the BSD license. You should have received
a copy of the file LICENSE.txt along with this software.

To test me, type:
python test_indent_finder.py 
python test_many_files.py

To install, type:
python setup.py install

See web page for more information: 
http://www.freehackers.org/Indent_Finder

History:
========

version 1.3:
- remove indent_checker, this was a useless program
- improve the indentation algorithm to be able to detecte mixed type indentation
- detect mixed type indentation, like the one used in vim source files

version 1.2:
- add indent_checker, to check the consistency of the indentation of a source tree

version 1.1:
- improve the heuristic by detecting indentation steps

version 1.0:
- initial release

