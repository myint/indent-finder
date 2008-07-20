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
from unittest import *
from pprint import pprint

class Test_find_indent( TestCase ):

    def test_re( self ):
        ifi = IndentFinder()
   
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

    def test_analyse_line_type( self ):
        ifi = IndentFinder()
        n = 1
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 2
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 3
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 4
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 5
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 6
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 7
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.BeginSpace, ' ' * n ) )
        n = 8
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.SpaceOnly, ' ' * n ) )
        n = 9
        self.assertEquals( ifi.analyse_line_type( ' ' * n + 'coucou' ), 
                            (LineType.SpaceOnly, ' ' * n ) )

        self.assertEquals( ifi.analyse_line_type( '\t' + 'coucou' ), 
                            (LineType.TabOnly, '\t' ) )

        self.assertEquals( ifi.analyse_line_type( '\t\t' + 'coucou' ), 
                            (LineType.TabOnly, '\t\t' ) )

        for i in range(1,8):
            self.assertEquals( ifi.analyse_line_type( '\t\t' + ' '*i + 'coucou' ), 
                                (LineType.Mixed, '\t\t', ' '*i ) )

        self.assertEquals( ifi.analyse_line_type( '\t\t' + ' ' * 9 + 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t\t \t' + 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '  \t\t' + 'coucou' ), None )

    def test_ignored_lines( self ):
        ifi = IndentFinder()

        self.assertEquals( ifi.analyse_line_type( '' ), None )
        self.assertEquals( ifi.analyse_line_type( '' ), None )
        self.assertEquals( ifi.analyse_line_type( '  ' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t' ), None )
        self.assertEquals( ifi.analyse_line_type( '\t  ' ), None )
        self.assertEquals( ifi.analyse_line_type( 'coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '  # coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '  /* coucou' ), None )
        self.assertEquals( ifi.analyse_line_type( '   * coucou' ), None )

        ifi.clear()
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

        ifi.clear()
        self.assertEquals( ifi.nb_processed_lines, 0)
        self.assertEquals( ifi.nb_indent_hint, 0)
        self.assertEquals( ifi.analyse_line( '  \n' ), None )
        self.assertEquals( ifi.analyse_line( '\t\n' ), None )
        self.assertEquals( ifi.analyse_line( '\t  \n' ), None )

    def test_analyse_line_tab( self ):
        ifi = IndentFinder()
        result = ifi.analyse_line( "" )
        result = ifi.analyse_line( "hop" )
        result = ifi.analyse_line( "\thop" )
        self.assertEquals( ifi.nb_indent_hint, 0 )

        result = ifi.analyse_line( "\t\thop" )
        self.assertEquals( result, 'tab' )
        self.assertEquals( ifi.lines['tab'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        result = ifi.analyse_line( "\t\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 1 )

        result = ifi.analyse_line( "\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 1 )

        result = ifi.analyse_line( "\t\t\thop" )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['tab'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

    def test_analyse_line_space2( self ):
        ifi = IndentFinder()
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '  hop' )
        self.assertEquals( ifi.nb_indent_hint, 0 )

        # indent
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, 'space2' )
        self.assertEquals( ifi.lines['space2'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        # same
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, None )

        # dedent
        result = ifi.analyse_line( "  hop" )
        self.assertEquals( result, None )

        # big indentation
        result = ifi.analyse_line( "      hop" )
        self.assertEquals( result, 'space4' )
        self.assertEquals( ifi.lines['space2'], 1 )

    def test_analyse_line_space4( self ):
        ifi = IndentFinder()
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( ifi.nb_indent_hint, 0 )

        # indent
        result = ifi.analyse_line( '        hop' )
        self.assertEquals( result, 'space4' )
        self.assertEquals( ifi.lines['space4'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        # same
        result = ifi.analyse_line( '        hop' )
        self.assertEquals( result, None )

        # dedent
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( result, None )

        # big indentation
        result = ifi.analyse_line( '            hop' )
        self.assertEquals( result, 'space8' )
        self.assertEquals( ifi.lines['space4'], 1 )

    def test_analyse_line_space8( self ):
        ifi = IndentFinder()
        idt = '        '  
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( idt+'hop' )
        self.assertEquals( ifi.nb_indent_hint, 0 )

        # indent
        result = ifi.analyse_line( idt*2+'hop' )
        self.assertEquals( result, 'space8' )
        self.assertEquals( ifi.lines['space8'], 1 )
        self.assertEquals( ifi.nb_indent_hint, 1 )

        # same
        result = ifi.analyse_line( idt*2+'hop' )
        self.assertEquals( result, None )

        # dedent
        result = ifi.analyse_line( idt+'hop' )
        self.assertEquals( result, None )

        # big indentation
        result = ifi.analyse_line( idt*3+'hop' )
        self.assertEquals( result, None )
        self.assertEquals( ifi.lines['space8'], 1 )


    def test_analyse_line_mixed( self ):
        ifi = IndentFinder()
        result = ifi.analyse_line( '' )
        result = ifi.analyse_line( 'hop' )
        result = ifi.analyse_line( '    hop' )
        self.assertEquals( ifi.nb_indent_hint, 0 )

        # indent
        result = ifi.analyse_line( '\thop' )
        self.assertEquals( result, 'mixed4' )

        result = ifi.analyse_line( '\t    hop' )
        self.assertEquals( result, 'mixed4' )

        result = ifi.analyse_line( '\t\thop' )
        self.assertEquals( result, 'mixed4' )

        self.assertEquals( ifi.nb_indent_hint, 3 )

        # same
        result = ifi.analyse_line( '\t\thop' )
        self.assertEquals( result, None )

        # dedent
        result = ifi.analyse_line( '\t    hop' )
        self.assertEquals( result, None )
        result = ifi.analyse_line( '\thop' )
        self.assertEquals( result, None )

        # big indentation
        result = ifi.analyse_line( '\t\t    hop' )
        self.assertEquals( result, None )
        result = ifi.analyse_line( '\t\t\t    hop' )
        self.assertEquals( result, None )

        self.assertEquals( ifi.nb_indent_hint, 3 )


if __name__ == "__main__":
    main( testRunner = TextTestRunner( verbosity = 2 ) )
