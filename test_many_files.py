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

    def test_file_DebugClient_py( self ):
        self.check_file( "test_files/DebugClient.py", 'space 4' )

    def test_file_diffmodel_cpp( self ):
        self.check_file( "test_files/diffmodel.cpp", 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_IOtest_java( self ):
        self.check_file( "test_files/IOtest.java", 'space 4')

    def test_file_pretty_make_py( self ):
        self.check_file( "test_files/pretty-make.py", 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_TestRunner_cpp( self ):
        self.check_file( "test_files/TestRunner.cpp", 'space 2' )

    def test_file_cml_py( self ):
        self.check_file( "test_files/cml.py", 'space 4' )

    def test_file_tab( self ):
        l = []
        l += glob.glob( 'test_files/tab/*.c' )
        for f in l:
            print 'checking: ', f
            self.check_file( f , 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_vim_files_c( self ):
        l = []
        l += glob.glob( 'test_files/mixed4/*.c' )
        for f in l:
            print 'checking: ', f
            self.check_file( f, 'mixed tab 8 space 4' )
        

if __name__ == "__main__":
    main( testRunner = TextTestRunner( verbosity = 2 ) )
