
from indent_finder import IndentFinder

from unittest import *

class Test_find_indent( TestCase ):

	def test_indent_re( self ):
		fi = IndentFinder()

		fi.clear()
		fi.analyse_line( "\t\t  hop" ) # skip mixed indentation
		self.assertEquals( fi.nb, 0 )

		fi.clear()
		fi.analyse_line( "\t\t  " ) # skip blank line
		self.assertEquals( fi.nb, 0 )

		fi.clear()
		fi.analyse_line( "\t\thop\\\n" )
		fi.analyse_line( "\t\tbof" ) # only one line when last char is \
		self.assertEquals( fi.nb, 1 )

		fi.clear()
		fi.analyse_line( "\t\thop" ) # take tab
		self.assertEquals( fi.nb, 1 )

		fi.clear()
		fi.analyse_line( "    hop" ) # take spaces
		self.assertEquals( fi.nb, 1 )

	def check_file( self, fname, result ):
		fi = IndentFinder()
		fi.parse_file( "Tests\\" + fname )
		res = str(fi)
		self.assertEquals( res, result )

	def test_debug_client_py( self ):
		self.check_file( "DebugClient.py", "space 4" )

	def test_diff_model_cpp( self ):
		self.check_file( "diffmodel.cpp", "tab 8" )

	def test_iotest_java( self ):
		self.check_file( "IOtest.java", "space 4" )

	def test_pretty_make_py( self ):
		self.check_file( "pretty-make.py", "tab 8" )

	def test_test_runner_py( self ):
		self.check_file( "TestRunner.cpp", "space 2" )

if __name__ == "__main__":
	main()
