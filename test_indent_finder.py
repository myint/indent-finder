#!/usr/bin/env python
# 
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002,2005 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.
#


from indent_finder import *

import os, glob
import unittest
from pprint import pprint

TEST_DEFAULT_RESULT=('',0)

class Test_find_indent( unittest.TestCase ):

    def test_indent_re( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
   
        mo = ifi.indent_re.match( '' )
        self.assertEquals( mo, None )
        mo = ifi.indent_re.match( '\t' )
        self.assertEquals( mo, None )
        mo = ifi.indent_re.match( '  ' )
        self.assertEquals( mo, None )
        mo = ifi.indent_re.match( '\t  ' )
        self.assertEquals( mo, None )

        mo = ifi.indent_re.match( ' x' )
        self.assertNotEquals( mo, None )
        self.assertEquals( mo.groups(), (' ', 'x' ) )

        mo = ifi.indent_re.match( '\tx' )
        self.assertNotEquals( mo, None )
        self.assertEquals( mo.groups(), ('\t', 'x' ) )

    def test_mixed_re( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
   
        mo = ifi.mixed_re.match( '' )
        self.assertEquals( mo, None )
        mo = ifi.mixed_re.match( '\t' )
        self.assertEquals( mo, None )
        mo = ifi.mixed_re.match( ' ' )
        self.assertEquals( mo, None )
        mo = ifi.mixed_re.match( ' \t' )
        self.assertEquals( mo, None )

        mo = ifi.mixed_re.match( '\t\t  ' )
        self.assertEquals( mo.group(1), '\t\t' )
        self.assertEquals( mo.group(2), '  ' )


    def test_analyse_line_type( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )

        for n in range(1,8):
            self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                                (LineType.BeginSpace, ' ' * n ) )
        for n in range(8,10):
            self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                                (LineType.SpaceOnly, ' ' * n ) )

        self.assertEquals( ifi.analyse_line_type( '\t' + 'coucou' ), 
                            (LineType.TabOnly, '\t' ) )

        self.assertEquals( ifi.analyse_line_type( '\t\t' + 'coucou' ), 
                            (LineType.TabOnly, '\t\t' ) )

        for i in range(1,8):
            self.assertEquals( ifi.analyse_line_type( '\t\t' + ' '*i + 'coucou' ), 
                                (LineType.Mixed, '\t\t', ' '*i ) )

        self.assertEquals( ifi.analyse_line_type( 'coucou' ), (LineType.NoIndent, '') )

        self.assertEquals( ifi.analyse_line_type( '' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t\t' + ' ' * 8 + 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t\t' + ' ' * 9 + 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t\t \t' + 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '  \t\t' + 'coucou' ), None )

    def test_ignored_lines_patterns( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )

        self.assertEquals( ifi.analyse_line_type( '' ), None )
        self.assertEquals( ifi.analyse_line_type( '  ' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t  ' ), None )
        self.assertEquals( ifi.analyse_line_type( '  # coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '  /* coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '   * coucou' ), None )

    def test_skip_next_line( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )

        self.assertEquals( ifi.nb_processed_lines, 0)
        self.assertEquals( ifi.nb_indent_hint, 0)
        self.assertEquals( ifi.analyse_line( '  coucou \n' ), None )
        self.assertEquals( ifi.skip_next_line, False )
        self.assertEquals( ifi.analyse_line( '    coucou \\\n' ), 'space2')
        self.assertEquals( ifi.skip_next_line, True )
        self.assertEquals( ifi.analyse_line( '      coucou\n' ), None )
        self.assertEquals( ifi.skip_next_line, False )
        self.assertEquals( ifi.nb_processed_lines, 3)
        self.assertEquals( ifi.nb_indent_hint, 1)

    def test_analyse_line_tab( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
        result = ifi.analyse_line( "" )
        result = ifi.analyse_line( "hop" )
        result = ifi.analyse_line( "\thop" )
        self.assertEquals( ifi.lines['tab'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        result = ifi.analyse_line( "\t\thop" )
        self.assertEquals( result, 'tab' )
        self.assertEquals( ifi.lines['tab'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        result = ifi.analyse_line( "\t\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 2 )

        result = ifi.analyse_line( "\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 2 )

        result = ifi.analyse_line( "\t\t\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

    def test_analyse_line_space2( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '  hop' )
        self.assertEquals( ifi.nb_indent_hint, 1 )
        self.assertEquals( ifi.lines['space2'], 1 )

        # indent
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, 'space2' )
        self.assertEquals( ifi.lines['space2'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # same
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # dedent
        result = ifi.analyse_line( "  hop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # big indentation
        result = ifi.analyse_line( "      hop" )
        self.assertEquals( result, 'space4' )
        self.assertEquals( ifi.lines['space2'], 2 )
        self.assertEquals( ifi.lines['space4'], 1 )

    def test_analyse_line_space4( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( ifi.nb_indent_hint, 1 )
        self.assertEquals( ifi.lines['space4'], 1 )

        # indent
        result = ifi.analyse_line( '        hop' )
        self.assertEquals( result, 'space4' )
        self.assertEquals( ifi.lines['space4'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # same
        result = ifi.analyse_line( '        hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # dedent
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # big indentation
        result = ifi.analyse_line( '            hop' )
        self.assertEquals( result, 'space8' )
        self.assertEquals( ifi.lines['space4'], 2 )
        self.assertEquals( ifi.lines['space8'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 3 )

    def test_analyse_line_space8( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
        idt = '        '  
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( idt+'hop' )
        self.assertEquals( ifi.lines['space8'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        # indent
        result = ifi.analyse_line( idt*2+'hop' )
        self.assertEquals( result, 'space8' )
        self.assertEquals( ifi.lines['space8'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # same
        result = ifi.analyse_line( idt*2+'hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # dedent
        result = ifi.analyse_line( idt+'hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        # big indentation is ignored
        result = ifi.analyse_line( idt*3+'hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['space8'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )


    def test_analyse_line_mixed( self ):
        ifi = IndentFinder( TEST_DEFAULT_RESULT )
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( ifi.nb_indent_hint, 1 )
        self.assertEquals( result, 'space4' )
        self.assertEquals( ifi.lines['mixed4'], 1 )
        self.assertEquals( ifi.lines['space4'], 1 )

        # indent
        result = ifi.analyse_line( '\thop' )
        self.assertEquals( result, 'mixed4' )
        self.assertEquals( ifi.lines['mixed4'], 2 )
        self.assertEquals( ifi.nb_indent_hint, 2 )

        result = ifi.analyse_line( '\t    hop' )
        self.assertEquals( result, 'mixed4' )
        self.assertEquals( ifi.lines['mixed4'], 3 )
        self.assertEquals( ifi.nb_indent_hint, 3 )

        result = ifi.analyse_line( '\t\thop' )
        self.assertEquals( result, 'mixed4' )
        self.assertEquals( ifi.lines['mixed4'], 4 )
        self.assertEquals( ifi.nb_indent_hint, 4 )

        # same
        result = ifi.analyse_line( '\t\thop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 4 )

        # dedent
        result = ifi.analyse_line( '\t    hop' )
        self.assertEquals( result, None )
        result = ifi.analyse_line( '\thop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.nb_indent_hint, 4 )

        # big indentation
        result = ifi.analyse_line( '\t\t    hop' )
        self.assertEquals( result, None )
        result = ifi.analyse_line( '\t\t\t    hop' )
        self.assertEquals( result, None )

        self.assertEquals( ifi.nb_indent_hint, 4 )

def main():
    unittest.main( testRunner = unittest.TextTestRunner( verbosity = 2 ) )

if __name__ == "__main__":
    main()
