#!/usr/bin/env python

from distutils.core import setup

import indent_finder


setup(name='Indentation Finder',
      version=indent_finder.VERSION,
      description='Finds of check the indentation used in programming source '
                  'files',
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
