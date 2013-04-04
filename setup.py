#!/usr/bin/env python
"""Installer for indent-finder."""

import ast
import os
from distutils import core

def version():
    """Return version string."""
    with open(os.path.join('plugin', 'indent_finder.py')) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    core.setup(
        name='indent-finder',
        version=version(),
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
        py_modules=['indent_finder'],
        package_dir={'': 'plugin'})
