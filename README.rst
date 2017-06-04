=============
indent-finder
=============

.. image:: https://travis-ci.org/myint/indent-finder.svg?branch=master
    :target: https://travis-ci.org/myint/indent-finder
    :alt: Build status

Copyright (C) 2002-2010 Philippe Fremy

Copyright (C) 2013-2017 Steven Myint

This program is distributed under the BSD license. You should have received
a copy of the file ``LICENSE.txt`` along with this software.


Introduction
============

indent-finder is a vim plugin that detects the indentation of a file and sets
vim's indentation settings appropriately to match.


Installation
============

Make sure ``set nocompatible`` is in your ``~/.vimrc``.

To install this plugin, copy the contents of the `plugin`_ directory to your
``~/.vim/plugin`` directory::

    $ git clone https://github.com/myint/indent-finder
    $ mkdir -p ~/.vim/plugin/
    $ cp -r ./indent-finder/plugin/* ~/.vim/plugin/

Or to install it using pathogen.vim_::

    $ cd ~/.vim/bundle
    $ git clone https://github.com/myint/indent-finder

.. _`pathogen.vim`: https://github.com/tpope/vim-pathogen
.. _`plugin`: https://github.com/myint/indent-finder/tree/master/plugin


Command-line usage
==================

To use from command line::

    $ ./indent_finder.py test_files/space1/one.cc
    space 1


History
=======

1.x
---

- Always use tabs for makefiles.

1.6.2
-----

- Clean up code.

1.6.1
-----

- Respect user's ``expandtab`` and ``shiftwidth`` settings.
- Detect indentation on all files and not just files with ``.`` in them.

1.6
---

- Support one-space indentation.

1.5.1
-----

- Improve performance.

1.5
---

- Simplify installation process.
- Detect when files have no valid indentation.
- Add Python 3 support.
- Default to user's ``tabstop`` when necessary.

1.4
---

- Improve the heuristic, some file where incorrectly reported as tab when being
  mixed.
- ``('tab', 4)`` was returned instead of ``DEFAULT_OUTPUT`` when no decision
  could be made. This is now configurable.
- ``vim_output()`` now includes a comment about the detected indentation.

1.31
----

- The --vim-output was not working. Fixed in this version.

1.3
---

- Remove indent_checker, this was a useless program.
- Improve the indentation algorithm to be able to detect mixed type
  indentation.
- Detect mixed type indentation, like the one used in Vim source files.

1.2
---

- Add indent_checker, to check the consistency of the indentation of a source
  tree.

1.1
---

- Improve the heuristic by detecting indentation steps.
