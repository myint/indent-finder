#!/usr/bin/env python
"""Installer for Indent Finder."""

from distutils import core

import indent_finder


with open('README.rst') as readme:
    core.setup(
        name='indentation-finder',
        version=indent_finder.__version__,
        description='Finds of check the indentation used in programming '
                    'source files',
        long_description=readme.read(),
        author='Philippe Fremy',
        author_email='phil at freehackers dot org',
        maintainer='Philippe Fremy',
        maintainer_email='phil at freehackers dot org',
        license='BSD license',
        url='http://www.freehackers.org/Indent_Finder',
        classifiers=['Intended Audience :: Developers',
                     'Environment :: Console',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3'],
        py_modules=['indent_finder'])
