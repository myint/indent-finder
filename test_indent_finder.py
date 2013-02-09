#!/usr/bin/env python
#
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002,2005 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.
#

import os
import subprocess
import unittest

import indent_finder


TEST_DEFAULT_RESULT = ('', 0)

ROOT_PATH = os.path.dirname(__file__)


class Tests(unittest.TestCase):

    def test_indent_re(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)

        mo = ifi.indent_re.match('')
        self.assertEquals(mo, None)
        mo = ifi.indent_re.match('\t')
        self.assertEquals(mo, None)
        mo = ifi.indent_re.match('  ')
        self.assertEquals(mo, None)
        mo = ifi.indent_re.match('\t  ')
        self.assertEquals(mo, None)

        mo = ifi.indent_re.match(' x')
        self.assertNotEquals(mo, None)
        self.assertEquals(mo.groups(), (' ', 'x'))

        mo = ifi.indent_re.match('\tx')
        self.assertNotEquals(mo, None)
        self.assertEquals(mo.groups(), ('\t', 'x'))

    def test_mixed_re(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)

        mo = ifi.mixed_re.match('')
        self.assertEquals(mo, None)
        mo = ifi.mixed_re.match('\t')
        self.assertEquals(mo, None)
        mo = ifi.mixed_re.match(' ')
        self.assertEquals(mo, None)
        mo = ifi.mixed_re.match(' \t')
        self.assertEquals(mo, None)

        mo = ifi.mixed_re.match('\t\t  ')
        self.assertEquals(mo.group(1), '\t\t')
        self.assertEquals(mo.group(2), '  ')

    def test_analyse_line_type(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)

        for n in range(1, 8):
            self.assertEquals(ifi.analyse_line_type(' ' * n + 'coucou'),
                             (indent_finder.LineType.BeginSpace, ' ' * n))
        for n in range(8, 10):
            self.assertEquals(ifi.analyse_line_type(' ' * n + 'coucou'),
                             (indent_finder.LineType.SpaceOnly, ' ' * n))

        self.assertEquals(ifi.analyse_line_type('\t' + 'coucou'),
                         (indent_finder.LineType.TabOnly, '\t'))

        self.assertEquals(ifi.analyse_line_type('\t\t' + 'coucou'),
                         (indent_finder.LineType.TabOnly, '\t\t'))

        for i in range(1, 8):
            self.assertEquals(
                ifi.analyse_line_type('\t\t' + ' ' * i + 'coucou'),
                (indent_finder.LineType.Mixed, '\t\t', ' ' * i))

        self.assertEquals(
            ifi.analyse_line_type('coucou'),
            (indent_finder.LineType.NoIndent, ''))

        self.assertEquals(ifi.analyse_line_type(''), None)
        self.assertEquals(
            ifi.analyse_line_type('\t\t' + ' ' * 8 + 'coucou'), None)
        self.assertEquals(
            ifi.analyse_line_type('\t\t' + ' ' * 9 + 'coucou'), None)
        self.assertEquals(ifi.analyse_line_type('\t\t \t' + 'coucou'), None)
        self.assertEquals(ifi.analyse_line_type('  \t\t' + 'coucou'), None)

    def test_ignored_lines_patterns(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)

        self.assertEquals(ifi.analyse_line_type(''), None)
        self.assertEquals(ifi.analyse_line_type('  '), None)
        self.assertEquals(ifi.analyse_line_type('\t'), None)
        self.assertEquals(ifi.analyse_line_type('\t  '), None)
        self.assertEquals(ifi.analyse_line_type('  # coucou'), None)
        self.assertEquals(ifi.analyse_line_type('  /* coucou'), None)
        self.assertEquals(ifi.analyse_line_type('   * coucou'), None)

    def test_skip_next_line(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)

        self.assertEquals(ifi.nb_processed_lines, 0)
        self.assertEquals(ifi.nb_indent_hint, 0)
        self.assertEquals(ifi.analyse_line('  coucou \n'), None)
        self.assertEquals(ifi.skip_next_line, False)
        self.assertEquals(ifi.analyse_line('    coucou \\\n'), 'space2')
        self.assertEquals(ifi.skip_next_line, True)
        self.assertEquals(ifi.analyse_line('      coucou\n'), None)
        self.assertEquals(ifi.skip_next_line, False)
        self.assertEquals(ifi.nb_processed_lines, 3)
        self.assertEquals(ifi.nb_indent_hint, 1)

    def test_analyse_line_tab(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)
        result = ifi.analyse_line("")
        result = ifi.analyse_line("hop")
        result = ifi.analyse_line("\thop")
        self.assertEquals(ifi.lines['tab'], 1)
        self.assertEquals(ifi.nb_indent_hint, 1)

        result = ifi.analyse_line("\t\thop")
        self.assertEquals(result, 'tab')
        self.assertEquals(ifi.lines['tab'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

        result = ifi.analyse_line("\t\thop")
        self.assertEquals(result, None)
        self.assertEquals(ifi.lines['tab'], 2)

        result = ifi.analyse_line("\thop")
        self.assertEquals(result, None)
        self.assertEquals(ifi.lines['tab'], 2)

        result = ifi.analyse_line("\t\t\thop")
        self.assertEquals(result, None)
        self.assertEquals(ifi.lines['tab'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

    def test_analyse_line_space2(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('  hop')
        self.assertEquals(ifi.nb_indent_hint, 1)
        self.assertEquals(ifi.lines['space2'], 1)

        # indent
        result = ifi.analyse_line('    hop')
        self.assertEquals(result, 'space2')
        self.assertEquals(ifi.lines['space2'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # same
        result = ifi.analyse_line('    hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # dedent
        result = ifi.analyse_line("  hop")
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # big indentation
        result = ifi.analyse_line("      hop")
        self.assertEquals(result, 'space4')
        self.assertEquals(ifi.lines['space2'], 2)
        self.assertEquals(ifi.lines['space4'], 1)

    def test_analyse_line_space4(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('    hop')
        self.assertEquals(ifi.nb_indent_hint, 1)
        self.assertEquals(ifi.lines['space4'], 1)

        # indent
        result = ifi.analyse_line('        hop')
        self.assertEquals(result, 'space4')
        self.assertEquals(ifi.lines['space4'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # same
        result = ifi.analyse_line('        hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # dedent
        result = ifi.analyse_line('    hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # big indentation
        result = ifi.analyse_line('            hop')
        self.assertEquals(result, 'space8')
        self.assertEquals(ifi.lines['space4'], 2)
        self.assertEquals(ifi.lines['space8'], 1)
        self.assertEquals(ifi.nb_indent_hint, 3)

    def test_analyse_line_space8(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)
        idt = '        '
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line(idt + 'hop')
        self.assertEquals(ifi.lines['space8'], 1)
        self.assertEquals(ifi.nb_indent_hint, 1)

        # indent
        result = ifi.analyse_line(idt * 2 + 'hop')
        self.assertEquals(result, 'space8')
        self.assertEquals(ifi.lines['space8'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # same
        result = ifi.analyse_line(idt * 2 + 'hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # dedent
        result = ifi.analyse_line(idt + 'hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 2)

        # big indentation is ignored
        result = ifi.analyse_line(idt * 3 + 'hop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.lines['space8'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

    def test_analyse_line_mixed(self):
        ifi = indent_finder.IndentFinder(TEST_DEFAULT_RESULT)
        result = ifi.analyse_line('')
        result = ifi.analyse_line('hop')
        result = ifi.analyse_line('    hop')
        self.assertEquals(ifi.nb_indent_hint, 1)
        self.assertEquals(result, 'space4')
        self.assertEquals(ifi.lines['mixed4'], 1)
        self.assertEquals(ifi.lines['space4'], 1)

        # indent
        result = ifi.analyse_line('\thop')
        self.assertEquals(result, 'mixed4')
        self.assertEquals(ifi.lines['mixed4'], 2)
        self.assertEquals(ifi.nb_indent_hint, 2)

        result = ifi.analyse_line('\t    hop')
        self.assertEquals(result, 'mixed4')
        self.assertEquals(ifi.lines['mixed4'], 3)
        self.assertEquals(ifi.nb_indent_hint, 3)

        result = ifi.analyse_line('\t\thop')
        self.assertEquals(result, 'mixed4')
        self.assertEquals(ifi.lines['mixed4'], 4)
        self.assertEquals(ifi.nb_indent_hint, 4)

        # same
        result = ifi.analyse_line('\t\thop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 4)

        # dedent
        result = ifi.analyse_line('\t    hop')
        self.assertEquals(result, None)
        result = ifi.analyse_line('\thop')
        self.assertEquals(result, None)
        self.assertEquals(ifi.nb_indent_hint, 4)

        # big indentation
        result = ifi.analyse_line('\t\t    hop')
        self.assertEquals(result, None)
        result = ifi.analyse_line('\t\t\t    hop')
        self.assertEquals(result, None)

        self.assertEquals(ifi.nb_indent_hint, 4)

    def test_system(self):
        process = subprocess.Popen(
            ['python', '-m', 'indent_finder',
             os.path.join(ROOT_PATH, 'test_files', 'tab', 'pretty-make.py')],
            stdout=subprocess.PIPE)

        self.assertEqual('tab 4\n', process.communicate()[0].decode('utf-8'))
        self.assertEqual(0, process.returncode)

    def test_system_with_vim_output(self):
        process = subprocess.Popen(
            ['python', '-m', 'indent_finder', '--vim-output',
             os.path.join(ROOT_PATH, 'test_files', 'tab', 'pretty-make.py')],
            stdout=subprocess.PIPE)

        self.assertEqual(
            'set sts=0 | set tabstop=4 | set noexpandtab | '
            'set shiftwidth=4 " (tab)',
            process.communicate()[0].decode('utf-8'))

        self.assertEqual(0, process.returncode)


def main():
    unittest.main(testRunner=unittest.TextTestRunner())

if __name__ == "__main__":
    main()
