indent-finder
=============

.. image:: https://travis-ci.org/myint/indent-finder.svg?branch=master
    :target: https://travis-ci.org/myint/indent-finder
    :alt: Build status

by Philippe Fremy <phil at freehackers dot org>

Copyright (C) 2002-2010 Philippe Fremy

Copyright (C) 2013 Steven Myint

This program is distributed under the BSD license. You should have received
a copy of the file LICENSE.txt along with this software.

History:
--------

version 1.5:

- Simplify installation process.
- Detect when files have no valid indentation.
- Add Python 3 support.
- Default to user's ``tabstop`` when necessary.

version 1.4:

- Improve the heuristic, some file where incorrectly reported as tab when being
  mixed.
- ('tab', 4) was returned instead of DEFAULT_OUTPUT when no decision could be
  made. This is now configurable.
- vim_output() now includes a comment about the detected indentation.

version 1.31:

- The --vim-output was not working. Fixed in this version.

version 1.3:

- Remove indent_checker, this was a useless program.
- Improve the indentation algorithm to be able to detecte mixed type
  indentation.
- Detect mixed type indentation, like the one used in vim source files.

version 1.2:

- Add indent_checker, to check the consistency of the indentation of a source
  tree.

version 1.1:

- Improve the heuristic by detecting indentation steps.

version 1.0:

- Initial release.
