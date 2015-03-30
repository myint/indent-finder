#!/usr/bin/env python
#
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002,2005 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.

import glob
import unittest

import indent_finder


TEST_DEFAULT_RESULT = (indent_finder.IndentType.space, 0)
TEST_DEFAULT_TAB_WIDTH = 13


class TestManyFiles(unittest.TestCase):

    def check_file(self, filename, result, expected_vim_result):
        ifi = indent_finder.IndentFinder()
        results = indent_finder._parse_file(
            ifi, filename,
            default_tab_width=TEST_DEFAULT_TAB_WIDTH,
            default_result=TEST_DEFAULT_RESULT)
        res = indent_finder.results_to_string(results)
        self.assertEqual(res, result, filename)
        self.assertEqual(
            expected_vim_result,
            indent_finder.vim_output(
                results,
                default_tab_width=TEST_DEFAULT_TAB_WIDTH))

    def test_file_space4(self):
        for f in glob.glob('test_files/space4/*'):
            self.check_file(
                f,
                'space 4',
                'set softtabstop=4 | set tabstop=4 | set expandtab | '
                'set shiftwidth=4 " (space 4)')

    def test_file_space2(self):
        for f in glob.glob('test_files/space2/*'):
            self.check_file(
                f,
                'space 2',
                'set softtabstop=2 | set tabstop=2 | set expandtab | '
                'set shiftwidth=2 " (space 2)')

    def test_file_space1(self):
        for f in glob.glob('test_files/space1/*'):
            self.check_file(
                f,
                'space 1',
                'set softtabstop=1 | set tabstop=1 | set expandtab | '
                'set shiftwidth=1 " (space 1)')

    def test_file_tab(self):
        for f in glob.glob('test_files/tab/*'):
            width = str(TEST_DEFAULT_TAB_WIDTH)
            self.check_file(
                f,
                'tab ' + width,
                'set softtabstop=0 | set tabstop=' + width +
                ' | set noexpandtab | set shiftwidth=' + width + ' " (tab)')

    def test_file_mixed4(self):
        for f in glob.glob('test_files/mixed4/*'):
            self.check_file(
                f,
                'mixed tab 8 space 4',
                'set softtabstop=0 | set tabstop=8 | set noexpandtab | '
                'set shiftwidth=4 " (mixed 4)')

    def test_file_default(self):
        for f in glob.glob('test_files/default/*'):
            default = str(TEST_DEFAULT_RESULT[1])

            self.check_file(
                f,
                'space ' + default,
                'set softtabstop=' + default + ' | set tabstop=' + default +
                ' | set expandtab | set shiftwidth=' + default +
                ' " (space ' + default + ')')


if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner())
