#!/usr/bin/env python
# 
# Indentation finder, by Philippe Fremy <phil at freehackers dot org>
# Copyright 2002,2005 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.
#


import indent_finder

import os, glob
import unittest 
from pprint import pprint

class Test_many_files( unittest.TestCase ):

    def check_file( self, fname, result, expected_vim_result ):
        ifi = indent_finder.IndentFinder()
        indent_finder.DEFAULT_TAB_WIDTH = 13
        ifi.parse_file( fname )
        res = str(ifi)
        self.assertEquals( res, result )
        self.assertEquals( expected_vim_result, ifi.vim_output() )

    def test_file_space4( self ):
        l = []
        l += glob.glob( 'test_files/space4/*.py' )
        l += glob.glob( 'test_files/space4/*.java' )
        l += glob.glob( 'test_files/space4/*.vim' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'space 4', 
              'set sts=4 | set tabstop=4 | set expandtab | set shiftwidth=4' )

    def test_file_space2( self ):
        l = []
        l += glob.glob( 'test_files/space2/*.cpp' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'space 2', 
              'set sts=2 | set tabstop=2 | set expandtab | set shiftwidth=2' )

    def test_file_tab( self ):
        l = []
        l += glob.glob( 'test_files/tab/*.c' )
        l += glob.glob( 'test_files/tab/*.cpp' )
        l += glob.glob( 'test_files/tab/*.py' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'tab %d' % indent_finder.DEFAULT_TAB_WIDTH,
            'set sts=0 | set tabstop=%d | set noexpandtab | set shiftwidth=%d'%
              (indent_finder.DEFAULT_TAB_WIDTH, 
                indent_finder.DEFAULT_TAB_WIDTH) )

    def test_file_mixed4( self ):
        l = []
        l += glob.glob( 'test_files/mixed4/*.c' )
        for f in l:
            print 'checking: ', f
            self.check_file( f, 'mixed tab 8 space 4',
              'set sts=4 | set tabstop=8 | set noexpandtab | set shiftwidth=4' )
        

if __name__ == "__main__":
    unittest.main( testRunner = unittest.TextTestRunner( verbosity = 2 ) )
