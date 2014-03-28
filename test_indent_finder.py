#!/usr/bin/env python
#
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002,2005 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.

import os
import subprocess
import sys
import unittest

import indent_finder


TEST_DEFAULT_RESULT = ('', 0)

ROOT_PATH = os.path.dirname(__file__)


class TestIndentFinder(unittest.TestCase):

    def test_indent_re(self):
        mo = indent_finder.INDENT_RE.match('')
        self.assertEqual(mo, None)
        mo = indent_finder.INDENT_RE.match('\t')
        self.assertEqual(mo, None)
        mo = indent_finder.INDENT_RE.match('  ')
        self.assertEqual(mo, None)
        mo = indent_finder.INDENT_RE.match('\t  ')
        self.assertEqual(mo, None)

        mo = indent_finder.INDENT_RE.match(' x')
        self.assertNotEqual(mo, None)
        self.assertEqual(mo.groups(), (' ', 'x'))

        mo = indent_finder.INDENT_RE.match('\tx')
        self.assertNotEqual(mo, None)
        self.assertEqual(mo.groups(), ('\t', 'x'))

    def test_mixed_re(self):
        mo = indent_finder.MIXED_RE.match('')
        self.assertEqual(mo, None)
        mo = indent_finder.MIXED_RE.match('\t')
        self.assertEqual(mo, None)
        mo = indent_finder.MIXED_RE.match(' ')
        self.assertEqual(mo, None)
        mo = indent_finder.MIXED_RE.match(' \t')
        self.assertEqual(mo, None)

        mo = indent_finder.MIXED_RE.match('\t\t  ')
        self.assertEqual(mo.group(1), '\t\t')
        self.assertEqual(mo.group(2), '  ')

    def test_analyse_line_type(self):
        for n in range(1, 8):
            self.assertEqual(
                indent_finder.analyse_line_type(' ' * n + 'coucou'),
                (indent_finder.LineType.BeginSpace, ' ' * n))

        for n in range(8, 10):
            self.assertEqual(
                indent_finder.analyse_line_type(' ' * n + 'coucou'),
                (indent_finder.LineType.SpaceOnly, ' ' * n))

        self.assertEqual(indent_finder.analyse_line_type('\t' + 'coucou'),
                         (indent_finder.LineType.TabOnly, '\t'))

        self.assertEqual(indent_finder.analyse_line_type('\t\t' + 'coucou'),
                         (indent_finder.LineType.TabOnly, '\t\t'))

        for i in range(1, 8):
            self.assertEqual(
                indent_finder.analyse_line_type('\t\t' + ' ' * i + 'coucou'),
                (indent_finder.LineType.Mixed, '\t\t', ' ' * i))

        self.assertEqual(
            indent_finder.analyse_line_type('coucou'),
            (indent_finder.LineType.NoIndent, ''))

        self.assertEqual(
            None, indent_finder.analyse_line_type(''))
        self.assertEqual(
            None, indent_finder.analyse_line_type('\t\t' + ' ' * 8 + 'coucou'))
        self.assertEqual(
            None, indent_finder.analyse_line_type('\t\t' + ' ' * 9 + 'coucou'))
        self.assertEqual(
            None, indent_finder.analyse_line_type('\t\t \t' + 'coucou'))
        self.assertEqual(
            None, indent_finder.analyse_line_type('  \t\t' + 'coucou'))

    def test_ignored_lines_patterns(self):
        self.assertEqual(indent_finder.analyse_line_type(''), None)
        self.assertEqual(indent_finder.analyse_line_type('  '), None)
        self.assertEqual(indent_finder.analyse_line_type('\t'), None)
        self.assertEqual(indent_finder.analyse_line_type('\t  '), None)
        self.assertEqual(indent_finder.analyse_line_type('  # coucou'), None)
        self.assertEqual(indent_finder.analyse_line_type('  /* coucou'), None)
        self.assertEqual(indent_finder.analyse_line_type('   * coucou'), None)

    def test_skip_next_line(self):
        ifi = indent_finder.IndentFinder()

        self.assertEqual(ifi.analyse_line('  coucou \n'), None)
        self.assertEqual(ifi.skip_next_line, False)
        self.assertEqual(ifi.analyse_line('    coucou \\\n'), 'space2')
        self.assertEqual(ifi.skip_next_line, True)
        self.assertEqual(ifi.analyse_line('      coucou\n'), None)
        self.assertEqual(ifi.skip_next_line, False)

    def test_analyse_line_tab(self):
        ifi = indent_finder.IndentFinder()
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('\thop')
        self.assertEqual(ifi.lines['tab'], 1)

        result = ifi.analyse_line('\t\thop')
        self.assertEqual(result, 'tab')
        self.assertEqual(ifi.lines['tab'], 2)

        result = ifi.analyse_line('\t\thop')
        self.assertEqual(result, None)
        self.assertEqual(ifi.lines['tab'], 2)

        result = ifi.analyse_line('\thop')
        self.assertEqual(result, None)
        self.assertEqual(ifi.lines['tab'], 2)

        result = ifi.analyse_line('\t\t\thop')
        self.assertEqual(result, None)
        self.assertEqual(ifi.lines['tab'], 2)

    def test_analyse_line_space2(self):
        ifi = indent_finder.IndentFinder()
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('  hop')
        self.assertEqual(ifi.lines['space2'], 1)

        # indent
        result = ifi.analyse_line('    hop')
        self.assertEqual(result, 'space2')
        self.assertEqual(ifi.lines['space2'], 2)

        # same
        result = ifi.analyse_line('    hop')
        self.assertEqual(result, None)

        # dedent
        result = ifi.analyse_line('  hop')
        self.assertEqual(result, None)

        # big indentation
        result = ifi.analyse_line('      hop')
        self.assertEqual(result, 'space4')
        self.assertEqual(ifi.lines['space2'], 2)
        self.assertEqual(ifi.lines['space4'], 1)

    def test_analyse_line_space4(self):
        ifi = indent_finder.IndentFinder()
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('    hop')
        self.assertEqual(ifi.lines['space4'], 1)

        # indent
        result = ifi.analyse_line('        hop')
        self.assertEqual(result, 'space4')
        self.assertEqual(ifi.lines['space4'], 2)

        # same
        result = ifi.analyse_line('        hop')
        self.assertEqual(result, None)

        # dedent
        result = ifi.analyse_line('    hop')
        self.assertEqual(result, None)

        # big indentation
        result = ifi.analyse_line('            hop')
        self.assertEqual(result, 'space8')
        self.assertEqual(ifi.lines['space4'], 2)
        self.assertEqual(ifi.lines['space8'], 1)

    def test_analyse_line_space8(self):
        ifi = indent_finder.IndentFinder()
        idt = '        '
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line(idt + 'hop')
        self.assertEqual(ifi.lines['space8'], 1)

        # indent
        result = ifi.analyse_line(idt * 2 + 'hop')
        self.assertEqual(result, 'space8')
        self.assertEqual(ifi.lines['space8'], 2)

        # same
        result = ifi.analyse_line(idt * 2 + 'hop')
        self.assertEqual(result, None)

        # dedent
        result = ifi.analyse_line(idt + 'hop')
        self.assertEqual(result, None)

        # big indentation is ignored
        result = ifi.analyse_line(idt * 3 + 'hop')
        self.assertEqual(result, None)
        self.assertEqual(ifi.lines['space8'], 2)

    def test_analyse_line_mixed(self):
        ifi = indent_finder.IndentFinder()
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('    hop')
        self.assertEqual(result, 'space4')
        self.assertEqual(ifi.lines['mixed4'], 1)
        self.assertEqual(ifi.lines['space4'], 1)

        # indent
        result = ifi.analyse_line('\thop')
        self.assertEqual(result, 'mixed4')
        self.assertEqual(ifi.lines['mixed4'], 2)

        result = ifi.analyse_line('\t    hop')
        self.assertEqual(result, 'mixed4')
        self.assertEqual(ifi.lines['mixed4'], 3)

        result = ifi.analyse_line('\t\thop')
        self.assertEqual(result, 'mixed4')
        self.assertEqual(ifi.lines['mixed4'], 4)

        # same
        result = ifi.analyse_line('\t\thop')
        self.assertEqual(result, None)

        # dedent
        result = ifi.analyse_line('\t    hop')
        self.assertEqual(result, None)
        result = ifi.analyse_line('\thop')
        self.assertEqual(result, None)

        # big indentation
        result = ifi.analyse_line('\t\t    hop')
        self.assertEqual(result, None)
        result = ifi.analyse_line('\t\t\t    hop')
        self.assertEqual(result, None)

    def test_system(self):
        process = subprocess.Popen(
            [sys.executable, './indent_finder.py', '--default-tab-width=7',
             os.path.join(ROOT_PATH, 'test_files', 'tab', 'pretty-make.py')],
            stdout=subprocess.PIPE)

        self.assertEqual('tab 7\n', process.communicate()[0].decode())
        self.assertEqual(0, process.returncode)

    def test_system_with_vim_output(self):
        process = subprocess.Popen(
            [sys.executable, './indent_finder.py', '--vim-output',
             os.path.join(ROOT_PATH, 'test_files', 'tab', 'pretty-make.py')],
            stdout=subprocess.PIPE)

        self.assertEqual(
            'set softtabstop=0 | set tabstop=8 | set noexpandtab | '
            'set shiftwidth=8 " (tab)',
            process.communicate()[0].decode())

        self.assertEqual(0, process.returncode)


if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner())
