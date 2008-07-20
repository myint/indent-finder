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
        ifi.VERBOSE = True
        ifi.parse_file( fname )
        res = str(ifi)
        self.assertEquals( res, result )

    def test_file_DebugClient_py( self ):
        self.check_file( "tests/DebugClient.py", 'space 4' )

    def test_file_diffmodel_cpp( self ):
        self.check_file( "tests/diffmodel.cpp", 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_IOtest_java( self ):
        self.check_file( "tests/IOtest.java", 'space 4')

    def test_file_pretty_make_py( self ):
        self.check_file( "tests/pretty-make.py", 'tab %d' % DEFAULT_TAB_WIDTH )

    def test_file_TestRunner_cpp( self ):
        self.check_file( "tests/TestRunner.cpp", 'space 2' )

    def test_file_cml_py( self ):
        self.check_file( "tests/cml.py", 'space 4' )

    def test_file_vim_files( self ):
        other_indent = [
            'dlldata.c',
            'nbdebug.c', 
            'os_w32dll.c', 
            'pathdef.c', 
            'wsdebug.c', 
            'iid_ole.c', 
            'integration.c', 
        ]

        l = []
        l += glob.glob( 'tests/vim_files/*.h' )
        # l += glob.glob( 'tests/vim_files/*.c' )
        for f in l:
            if os.path.basename( f ) in other_indent:
                print 'ignoring: ', f
                # special check
                pass
            else:
                print 'checking: ', f
                try:
                    self.check_file( f, 'mixed tab 8 space 4' )
                except AssertionError:
                    print 'Error!'
        

if __name__ == "__main__":
    main( testRunner = TextTestRunner( verbosity = 2 ) )
