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

class Test_many_files( TestCase ):

    def check_file( self, fname, result ):
        ifi = IndentFinder()
        ifi.parse_file( fname )
        res = str(ifi)
        self.assertEquals( res, result )

    def test_file_space4( self ):
        l = []
        l += glob.glob( 'test_files/space4/*.py' )
        l += glob.glob( 'test_files/space4/*.java' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'space 4' )

    def test_file_space2( self ):
        l = []
        l += glob.glob( 'test_files/space2/*.cpp' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'space 2' )

    def test_file_tab( self ):
        l = []
        l += glob.glob( 'test_files/tab/*.c' )
        l += glob.glob( 'test_files/tab/*.cpp' )
        l += glob.glob( 'test_files/tab/*.py' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_mixed4( self ):
        l = []
        l += glob.glob( 'test_files/mixed4/*.c' )
        for f in l:
            print 'checking: ', f
            self.check_file( f, 'mixed tab 8 space 4' )
        

if __name__ == "__main__":
    main( testRunner = TextTestRunner( verbosity = 2 ) )
