Indentation Finder
==================

.. image:: https://travis-ci.org/myint/IndentFinder.png?branch=master
   :target: https://travis-ci.org/myint/IndentFinder
   :alt: Build status

by Philippe Fremy <phil at freehackers dot org>
Copyright 2002-2010 Philippe Fremy

This program is distributed under the BSD license. You should have received
a copy of the file LICENSE.txt along with this software.

To test me, type::

    $ python run_tests.py

To install, type::

    $ pip install git+https://github.com/myint/indent-finder.git

And append the contents of `indent_finder.vim`_ to your ``.vimrc``.

.. _`indent_finder.vim`: https://raw.github.com/myint/IndentFinder/master/indent_finder.vim

To use from command line::

    $ python -m indent_finder example.py
    space 4

See `web page`_ for more information.

.. _`web page`: http://www.freehackers.org/Indent_Finder

History:
--------

version 1.4:

- improve the heuristic, some file where incorrectly reported as tab when being mixed
- ('tab', 4) was returned instead of DEFAULT_OUTPUT when no decision could be made. This is now
  configurable.
- vim_output() now includes a comment about the detected indentation

version 1.31:

- the --vim-output was not working. Fixed in this version

version 1.3:

- remove indent_checker, this was a useless program
- improve the indentation algorithm to be able to detecte mixed type
  indentation
- detect mixed type indentation, like the one used in vim source files

version 1.2:

- add indent_checker, to check the consistency of the indentation of a source
  tree

version 1.1:

- improve the heuristic by detecting indentation steps

version 1.0:

- initial release
