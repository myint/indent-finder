#!/usr/bin/env python
#
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright (C) 2002-2010 Philippe Fremy
# Copyright (C) 2013-2015 Steven Myint
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.

"""indent_finder.py

Display indentation used in the list of files. Possible answers are (with X
being the number of spaces used for indentation):
space X
tab 8
mixed tab X space Y

Mixed means that indentation style is tab at the beginning of the line (tab
being 8 positions) and then spaces to do the indentation, unless you reach 8
spaces which are replaced by a tab. This is the vim source file indentation
for example. In my opinion, this is the worst possible style.

"""

from __future__ import division

import optparse
import re
import sys


__version__ = '1.6.2'


INDENT_RE = re.compile('^([ \t]+)([^ \t]+)')
MIXED_RE = re.compile('^(\t+)( +)$')

MAX_BYTES = 100000

MIN_SPACES = 1
MAX_SPACES = 8

assert 0 < MIN_SPACES < MAX_SPACES

# Optionally used to fall back to default if pre-indentation line is not found.
# This is not used by the main line detection algorithm.
LANGUAGE_PRE_INDENTATION = {
    '.C': '{',
    '.c': '{',
    '.cc': '{',
    '.cpp': '{',
    '.h': '{',
    '.hpp': '{',
    '.py': ':',
}

BLACKLISTED_EXTENSIONS = ['.rst']


class IndentType(object):

    space = 'space'
    tab = 'tab'
    mixed = 'mixed'


def parse_file(filename,
               default_tab_width,
               default_result):
    """Return result of indentation analysis.

    Interpret with results_to_string() or vim_output().

    """
    return _parse_file(IndentFinder(),
                       filename=filename,
                       default_tab_width=default_tab_width,
                       default_result=default_result)


def _parse_file(finder, filename, default_tab_width, default_result):
    for extension in BLACKLISTED_EXTENSIONS:
        if filename.endswith(extension):
            return default_result

    required_ending = None
    for extension, ending in LANGUAGE_PRE_INDENTATION.items():
        if filename.endswith(extension):
            required_ending = ending

    finder.clear()
    found_required_ending = False
    for line in forcefully_read_lines(filename, MAX_BYTES):
        finder.analyse_line(line)

        if required_ending and line.rstrip().endswith(required_ending):
            found_required_ending = True

    if required_ending and not found_required_ending:
        return default_result

    return results(finder.lines,
                   default_tab_width=default_tab_width,
                   default_result=default_result)


class LineType(object):

    no_indent = 'no_indent'
    space_only = 'space_only'
    tab_only = 'tab_only'
    mixed = 'mixed'
    begin_space = 'begin_space'


class IndentFinder(object):

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
    - space_only: indentation of more than MAX_SPACES space
    - tab_only: indentation of tab only
    - mixed: indentation of tab, then less than MAX_SPACES spaces
    - begin_space: indentation of less than MAX_SPACES space, that could be
      either a mixed indentation or a pure space indentation.
    - non-significant

    Then two consecutive significant lines are then considered. The only valid
    combinations are:
    - (no_indent, begin_space)    => space or mixed
    - (no_indent, tab)            => tab
    - (begin_space, begin_space)  => space or mixed
    - (begin_space, space_only)   => space
    - (space_only, space_only)    => space
    - (tab_only, tab_only)        => tab
    - (tab_only, mixed)           => mixed
    - (mixed, tab_only)           => mixed

    The increment in number of spaces is then recorded.

    At the end, the number of lines with space indentation, mixed space and tab
    indentation are compared and a decision is made.

    If no decision can be made, None is returned.

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
        for i in range(MIN_SPACES, MAX_SPACES + 1):
            self.lines['space%d' % i] = 0
        for i in range(MIN_SPACES, MAX_SPACES + 1):
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
        if (
            t == (LineType.tab_only, LineType.tab_only) or
            t == (LineType.no_indent, LineType.tab_only)
        ):
            if len(current_line_info[1]) - len(previous_line_info[1]) == 1:
                self.lines['tab'] += 1
                return IndentType.tab

        elif (t == (LineType.space_only, LineType.space_only) or
              t == (LineType.begin_space, LineType.space_only) or
              t == (LineType.no_indent, LineType.space_only)):
            nb_space = len(current_line_info[1]) - len(previous_line_info[1])
            if MIN_SPACES <= nb_space <= MAX_SPACES:
                key = 'space%d' % nb_space
                self.lines[key] += 1
                return key

        elif (t == (LineType.begin_space, LineType.begin_space) or
              t == (LineType.no_indent, LineType.begin_space)):
            nb_space = len(current_line_info[1]) - len(previous_line_info[1])
            if MIN_SPACES <= nb_space <= MAX_SPACES:
                key1 = 'space%d' % nb_space
                key2 = 'mixed%d' % nb_space
                self.lines[key1] += 1
                self.lines[key2] += 1
                return key1

        elif t == (LineType.begin_space, LineType.tab_only):
            # We assume that mixed indentation used MAX_SPACES characters tabs.
            if len(current_line_info[1]) == 1:
                # More than one tab on the line --> not mixed mode!
                nb_space = (
                    len(current_line_info[1]) *
                    MAX_SPACES - len(previous_line_info[1])
                )
                if MIN_SPACES <= nb_space <= MAX_SPACES:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key

        elif t == (LineType.tab_only, LineType.mixed):
            (_, tab_part, space_part) = current_line_info
            if len(previous_line_info[1]) == len(tab_part):
                nb_space = len(space_part)
                if MIN_SPACES <= nb_space <= MAX_SPACES:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key

        elif t == (LineType.mixed, LineType.tab_only):
            (_, tab_part, space_part) = previous_line_info
            if len(tab_part) + 1 == len(current_line_info[1]):
                nb_space = MAX_SPACES - len(space_part)
                if MIN_SPACES <= nb_space <= MAX_SPACES:
                    key = 'mixed%d' % nb_space
                    self.lines[key] += 1
                    return key
        else:
            pass

        return None


def results(lines,
            default_tab_width,
            default_result):
    """Return analysis results.

    1. Space indented file
       - lines indented with less than MAX_SPACES space will fill mixed and
         space array
       - lines indented with MAX_SPACES space or more will fill only the space
         array
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
       - some lines are tab-only (lines with exactly MAX_SPACES step
         indentation)
       - some lines are space only (less than MAX_SPACES space)
       - all other lines are mixed

    If mixed is tab + 2 space indentation:
        - a lot more lines with mixed than with tab
    If mixed is tab + 4 space indentation
        - as many lines with mixed than with tab

    If no lines exceed MAX_SPACES space, there will be only lines with space
    and tab but no lines with mixed. Impossible to detect mixed indentation
    in this case, the file looks like it's actually indented as space only
    and will be detected so.

    => same or more lines with mixed than lines with tab only
    => same or more lines with mixed than lines with space only

    """
    max_line_space = max(
        [lines['space%d' % i] for i in range(MIN_SPACES, MAX_SPACES + 1)])
    max_line_mixed = max(
        [lines['mixed%d' % i] for i in range(MIN_SPACES, MAX_SPACES + 1)])
    max_line_tab = lines['tab']

    result = None

    # Detect space indented file.
    if max_line_space >= max_line_mixed and max_line_space > max_line_tab:
        nb = 0
        indent_value = None
        for i in range(MAX_SPACES, MIN_SPACES - 1, -1):
            # Give a 10% threshold.
            if lines['space%d' % i] > int(nb * 1.1):
                indent_value = i
                nb = lines['space%d' % indent_value]

        if indent_value is not None:
            result = (IndentType.space, indent_value)

    # Detect tab files.
    elif max_line_tab > max_line_mixed and max_line_tab > max_line_space:
        result = (IndentType.tab, default_tab_width)

    # Detect mixed files.
    elif (max_line_mixed >= max_line_tab and
          max_line_mixed > max_line_space):
        nb = 0
        indent_value = None
        for i in range(MAX_SPACES, 1, -1):
            # Give a 10% threshold.
            if lines['mixed%d' % i] > int(nb * 1.1):
                indent_value = i
                nb = lines['mixed%d' % indent_value]

        if indent_value is not None:
            result = (IndentType.mixed, (MAX_SPACES, indent_value))

    return result or default_result


def results_to_string(result_data):
    (indent_type, indent_value) = result_data
    if indent_type != IndentType.mixed:
        return '%s %d' % (indent_type, indent_value)
    else:
        (tab, space) = indent_value
        return '%s tab %d space %d' % (indent_type, tab, space)


def vim_output(result_data, default_tab_width):
    (indent_type, n) = result_data
    if indent_type == IndentType.space:
        return ('set softtabstop=%d | set tabstop=%d | set expandtab | '
                'set shiftwidth=%d " (%s %d)' % (n, n, n, indent_type, n))
    elif indent_type == IndentType.tab:
        return ('set softtabstop=0 | set tabstop=%d | set noexpandtab | '
                'set shiftwidth=%d " (%s)' %
                (default_tab_width, default_tab_width, indent_type))
    else:
        assert indent_type == IndentType.mixed

        (tab_indent, space_indent) = n
        return ('set softtabstop=0 | set tabstop=%d | set noexpandtab | '
                'set shiftwidth=%d " (%s %d)' %
                (tab_indent, space_indent, indent_type, space_indent))


def forcefully_read_lines(filename, size):
    """Return lines from file.

    Ignore UnicodeDecodeErrors.

    """
    input_file = open(filename, mode='rb')
    try:
        return input_file.read(size).decode('utf-8', 'replace').splitlines()
    finally:
        input_file.close()
    return []


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
        return (LineType.no_indent, '')

    mo = INDENT_RE.match(line)
    if not mo:
        return None

    indent_part = mo.group(1)
    text_part = mo.group(2)

    if text_part[0] == '*':
        # Continuation of a C/C++ comment, unlikely to be indented
        # correctly.
        return None

    if text_part[0:2] == '/*' or text_part[0] == '#':
        # Python, C/C++ comment, might not be indented correctly.
        return None

    if '\t' in indent_part and ' ' in indent_part:
        # Mixed mode.
        mo = MIXED_RE.match(indent_part)
        if not mo:
            # Line is not composed of '\t\t\t    ', ignore it.
            return None
        mixed_mode = True
        tab_part = mo.group(1)
        space_part = mo.group(2)

    if mixed_mode:
        if len(space_part) >= MAX_SPACES:
            # This is not mixed mode, this is garbage!
            return None
        return (LineType.mixed, tab_part, space_part)

    if '\t' in indent_part:
        return (LineType.tab_only, indent_part)

    assert ' ' in indent_part

    if len(indent_part) < MAX_SPACES:
        # This could be mixed mode too.
        return (LineType.begin_space, indent_part)
    else:
        # This is really a line indented with spaces.
        return (LineType.space_only, indent_part)


def main():
    parser = optparse.OptionParser(
        version='indent_finder.py %s' % (__version__,))

    parser.add_option('--vim-output', action='store_true',
                      help='output suitable to use inside vim')
    parser.add_option('--default-tab-width', type=int,
                      default=8,
                      help='default tab width (%default)')
    parser.add_option('--default-spaces', type=int,
                      default=4,
                      help='default indentation width (%default)')
    parser.add_option('--default-to-tabs', action='store_true',
                      help='default to tabs')

    (options, args) = parser.parse_args()

    if options.default_to_tabs:
        default_result = (IndentType.tab, options.default_tab_width)
    else:
        default_result = (IndentType.space, options.default_spaces)

    for filename in args:
        try:
            result_data = parse_file(
                filename,
                default_tab_width=options.default_tab_width,
                default_result=default_result)

            if options.vim_output:
                output = vim_output(
                    result_data,
                    default_tab_width=options.default_tab_width)
            else:
                output = results_to_string(result_data) + '\n'

            if len(args) > 1:
                output = filename + ' : ' + output.rstrip() + '\n'

            sys.stdout.write(output)
        except IOError:
            # Only print error message in non-Vim mode. Otherwise, we will be
            # passing garbage to Vim.
            if not options.vim_output:
                sys.stderr.write('%s\n' % (sys.exc_info()[1],))


if __name__ == '__main__':
    sys.exit(main())
