# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002-2008 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.

"""Usage : indent_finder.py [ --vim-output ] [file [file ...]]

Display indentation used in the list of files. Possible answers are (with X
being the number of spaces used for indentation):
space X
tab 8
mixed tab X space Y

mixed means that indentation style is tab at the beginning of the line (tab
being 8 positions) and then spaces to do the indentation, unless you reach 8
spaces which are replaced by a tab. This is the vim source file indentation
for example. In my opinion, this is the worst possible style.

"""

from __future__ import print_function

import optparse
import re
import sys


__version__ = '1.4'

# Used when indentation is tab, to set tabstop in vim.
DEFAULT_TAB_WIDTH = 4

# Default values for files where indentation is not meaningful (empty files).
DEFAULT_RESULT = ('space', 4)

INDENT_RE = re.compile('^([ \t]+)([^ \t]+)')
MIXED_RE = re.compile('^(\t+)( +)$')


def parse_file(finder, filename, default_result=DEFAULT_RESULT):
    is_python = filename.endswith('.py')

    finder.clear()
    found_python_indent = False
    for line in forcefully_read_lines(filename):
        finder.analyse_line(line)

        if is_python and line.rstrip().endswith(':'):
            found_python_indent = True

    if is_python and not found_python_indent:
        return default_result

    return results(finder.lines, default_result)


class LineType:
    NoIndent = 'NoIndent'
    SpaceOnly = 'SpaceOnly'
    TabOnly = 'TabOnly'
    Mixed = 'Mixed'
    BeginSpace = 'BeginSpace'


class IndentFinder:

    r"""IndentFinder reports the indentation used in a source file.

    Its approach is not tied to any particular language. It was tested
    successfully with python, C, C++ and Java code.

    How does it work?

    It scans each line of the entry file for a space character (white space or
    tab) repeated until a non space character is found. Such a line is
    considered to be a properly indented line of code. Blank lines and comments
    line (starting with # or /* or *) are ignored. Lines coming after a line
    ending in '\' have higher chance of being not properly indented, and are
    thus ignored too.

    Only the increment in indentation are fed in. Dedentation or maintaining
    the same indentation is not taken into account when analysing a file.
    Increment in indentation from zero indentation to some indentation is also
    ignored because it's wrong in many cases (header file with many structures
    for example, do not always obey the indentation of the rest of the code).

    Each line is analysed as:
    - SpaceOnly: indentation of more than 8 space
    - TabOnly: indentation of tab only
    - Mixed: indentation of tab, then less than 8 spaces
    - BeginSpace: indentation of less than 8 space, that could be either a
      mixed indentation or a pure space indentation.
    - non-significant

    Then two consecutive significant lines are then considered. The only valid
    combinations are:
    - (NoIndent, BeginSpace)    => space or mixed
    - (NoIndent, Tab)           => tab
    - (BeginSpace, BeginSpace)  => space or mixed
    - (BeginSpace, SpaceOnly)   => space
    - (SpaceOnly, SpaceOnly)    => space
    - (TabOnly, TabOnly)        => tab
    - (TabOnly, Mixed)          => mixed
    - (Mixed, TabOnly)          => mixed

    The increment in number of spaces is then recorded.

    At the end, the number of lines with space indentation, mixed space and tab
    indentation are compared and a decision is made.

    If no decision can be made, DEFAULT_RESULT is returned.

    If IndentFinder ever reports wrong indentation, send me immediately a
    mail, if possible with the offending file.

    """

    def __init__(self):
        self.skip_next_line = False
        self.previous_line_info = None
        self.lines = {}

        self.clear()

    def clear(self):
        self.lines = {}
        for i in range(2, 9):
            self.lines['space%d' % i] = 0
        for i in range(2, 9):
            self.lines['mixed%d' % i] = 0
        self.lines['tab'] = 0

        self.skip_next_line = False
        self.previous_line_info = None

    def analyse_line(self, line):
        if line[-1:] == '\n':
            line = line[:-1]

        skip_current_line = self.skip_next_line
        self.skip_next_line = False
        if line[-1:] == '\\':
            # skip lines after lines ending in \
            self.skip_next_line = True

        if skip_current_line:
            return

        ret = self.analyse_line_indentation(line)
        return ret

    def analyse_line_indentation(self, line):
        previous_line_info = self.previous_line_info
        current_line_info = analyse_line_type(line)
        self.previous_line_info = current_line_info

        if current_line_info is None or previous_line_info is None:
            return

        t = (previous_line_info[0], current_line_info[0])
        if (t == (LineType.TabOnly, LineType.TabOnly)
                or t == (LineType.NoIndent, LineType.TabOnly)):
            if len(current_line_info[1]) - len(previous_line_info[1]) == 1:
                self.lines['tab'] += 1
                return 'tab'

        elif (t == (LineType.SpaceOnly, LineType.SpaceOnly)
              or t == (LineType.BeginSpace, LineType.SpaceOnly)
              or t == (LineType.NoIndent, LineType.SpaceOnly)):
            nb_space = len(current_line_info[1]) - len(previous_line_info[1])
            if 1 < nb_space <= 8:
                key = 'space%d' % nb_space
                self.lines[key] += 1
                return key

        elif (t == (LineType.BeginSpace, LineType.BeginSpace)
              or t == (LineType.NoIndent, LineType.BeginSpace)):
            nb_space = len(current_line_info[1]) - len(previous_line_info[1])
            if 1 < nb_space <= 8:
                key1 = 'space%d' % nb_space
                key2 = 'mixed%d' % nb_space
                self.lines[key1] += 1
                self.lines[key2] += 1
                return key1

        elif t == (LineType.BeginSpace, LineType.TabOnly):
            # we assume that mixed indentation used 8 characters tabs
            if len(current_line_info[1]) == 1:
                # more than one tab on the line --> not mixed mode !
                nb_space = len(
                    current_line_info[1]) * 8 - len(previous_line_info[1])
                if 1 < nb_space <= 8:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key

        elif t == (LineType.TabOnly, LineType.Mixed):
            tab_part, space_part = tuple(current_line_info[1:3])
            if len(previous_line_info[1]) == len(tab_part):
                nb_space = len(space_part)
                if 1 < nb_space <= 8:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key

        elif t == (LineType.Mixed, LineType.TabOnly):
            tab_part, space_part = previous_line_info[1:3]
            if len(tab_part) + 1 == len(current_line_info[1]):
                nb_space = 8 - len(space_part)
                if 1 < nb_space <= 8:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key
        else:
            pass

        return None


def results(lines, default_result=DEFAULT_RESULT):
    """Return analysis results.

    1. Space indented file
       - lines indented with less than 8 space will fill mixed and space
         array
       - lines indented with 8 space or more will fill only the space array
       - almost no lines indented with tab

    => more lines with space than lines with mixed
    => more a lot more lines with space than tab

    2. Tab indented file
       - most lines will be tab only
       - very few lines as mixed
       - very few lines as space only

    => a lot more lines with tab than lines with mixed
    => a lot more lines with tab than lines with space

    3. Mixed tab/space indented file
       - some lines are tab-only (lines with exactly 8 step indentation)
       - some lines are space only (less than 8 space)
       - all other lines are mixed

    If mixed is tab + 2 space indentation:
        - a lot more lines with mixed than with tab
    If mixed is tab + 4 space indentation
        - as many lines with mixed than with tab

    If no lines exceed 8 space, there will be only lines with space
    and tab but no lines with mixed. Impossible to detect mixed indentation
    in this case, the file looks like it's actually indented as space only
    and will be detected so.

    => same or more lines with mixed than lines with tab only
    => same or more lines with mixed than lines with space only

    """
    max_line_space = max(
        [lines['space%d' % i] for i in range(2, 9)])
    max_line_mixed = max(
        [lines['mixed%d' % i] for i in range(2, 9)])
    max_line_tab = lines['tab']

    result = None

    # Detect space indented file
    if max_line_space >= max_line_mixed and max_line_space > max_line_tab:
        nb = 0
        indent_value = None
        for i in range(8, 1, -1):
            # Give a 10% threshold.
            if lines['space%d' % i] > int(nb * 1.1):
                indent_value = i
                nb = lines['space%d' % indent_value]

        if indent_value is None:  # no lines
            result = default_result
        else:
            result = ('space', indent_value)

    # Detect tab files
    elif max_line_tab > max_line_mixed and max_line_tab > max_line_space:
        result = ('tab', DEFAULT_TAB_WIDTH)

    # Detect mixed files
    elif (max_line_mixed >= max_line_tab and
          max_line_mixed > max_line_space):
        nb = 0
        indent_value = None
        for i in range(8, 1, -1):
            # Give a 10% threshold.
            if lines['mixed%d' % i] > int(nb * 1.1):
                indent_value = i
                nb = lines['mixed%d' % indent_value]

        if indent_value is None:  # no lines
            result = default_result
        else:
            result = ('mixed', (8, indent_value))

    else:
        # not enough information to make a decision
        result = default_result

    return result


def results_to_string(result_data):
    (itype, ival) = result_data
    if itype != 'mixed':
        return '%s %d' % (itype, ival)
    else:
        itab, ispace = ival
        return '%s tab %d space %d' % (itype, itab, ispace)


def vim_output(result_data):
    (indent_type, n) = result_data
    if indent_type == 'space':
        # spaces:
        #   => set sts to the number of spaces
        #   => set tabstop to the number of spaces
        #   => expand tabs to spaces
        #   => set shiftwidth to the number of spaces
        return ('set sts=%d | set tabstop=%d | set expandtab | '
                'set shiftwidth=%d " (%s %d)' % (n, n, n, indent_type, n))

    elif indent_type == 'tab':
        # tab:
        #   => set sts to 0
        #   => set tabstop to preferred value
        #   => set expandtab to false
        #   => set shiftwidth to tabstop
        return ('set sts=0 | set tabstop=%d | set noexpandtab | '
                'set shiftwidth=%d " (%s)' %
                (DEFAULT_TAB_WIDTH, DEFAULT_TAB_WIDTH, indent_type))

    if indent_type == 'mixed':
        tab_indent, space_indent = n
        # tab:
        #   => set sts to 0
        #   => set tabstop to tab_indent
        #   => set expandtab to false
        #   => set shiftwidth to space_indent
        return ('set sts=4 | set tabstop=%d | set noexpandtab | '
                'set shiftwidth=%d " (%s %d)'
                % (tab_indent, space_indent, indent_type, space_indent))


def forcefully_read_lines(filename):
    """Return lines from file.

    Ignore UnicodeDecodeErrors.

    """
    with open(filename) as f:
        line = None
        while line is None or line:
            # Line will only be '' on reaching the end.
            try:
                line = f.readline()
            except UnicodeDecodeError:
                continue

            yield line


def analyse_line_type(line):
    """Analyse the type of line.

    Return (LineType, <indentation part of the line>).

    The function will reject improperly formatted lines (mixture of tab
    and space for example) and comment lines.

    """
    mixed_mode = False
    tab_part = ''
    space_part = ''

    if len(line) > 0 and line[0] != ' ' and line[0] != '\t':
        return (LineType.NoIndent, '')

    mo = INDENT_RE.match(line)
    if not mo:
        return None

    indent_part = mo.group(1)
    text_part = mo.group(2)

    if text_part[0] == '*':
        # continuation of a C/C++ comment, unlikely to be indented
        # correctly
        return None

    if text_part[0:2] == '/*' or text_part[0] == '#':
        # python, C/C++ comment, might not be indented correctly
        return None

    if '\t' in indent_part and ' ' in indent_part:
        # mixed mode
        mo = MIXED_RE.match(indent_part)
        if not mo:
            # line is not composed of '\t\t\t    ', ignore it
            return None
        mixed_mode = True
        tab_part = mo.group(1)
        space_part = mo.group(2)

    if mixed_mode:
        if len(space_part) >= 8:
            # this is not mixed mode, this is garbage !
            return None
        return (LineType.Mixed, tab_part, space_part)

    if '\t' in indent_part:
        return (LineType.TabOnly, indent_part)

    assert ' ' in indent_part

    if len(indent_part) < 8:
        # this could be mixed mode too
        return (LineType.BeginSpace, indent_part)
    else:
        # this is really a line indented with spaces
        return (LineType.SpaceOnly, indent_part)


def main():
    parser = optparse.OptionParser(
        usage=__doc__.strip(),
        version='indent_finder: %s' % (__version__,))

    parser.add_option('--vim-output', action='store_true',
                      help='output suitable to use inside vim')

    options, args = parser.parse_args()

    fi = IndentFinder()

    one_file = (len(args) == 1)

    for filename in args:
        result_data = parse_file(fi, filename)

        if not one_file:
            if options.vim_output:
                print('%s : %s' % (filename, vim_output(result_data)))
            else:
                print('%s : %s' % (filename, results_to_string(result_data)))

    if one_file:
        if options.vim_output:
            sys.stdout.write(vim_output(result_data))
        else:
            print(results_to_string(result_data))


if __name__ == '__main__':
    sys.exit(main())
