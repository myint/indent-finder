# 
# Indentation finder, by Philippe Fremy <pfremy@freehackers.org>
#
# Copyright 2002 Philippe Fremy
#
# This program is distributed under the BSD license. You should have received
# a copy of the file LICENSE.txt along with this software.
#
# $Id$
#

import sys
import re

help = \
"""Usage : %s [ --separate ] [ --vim-output ] file1 file2 ... fileN

Display indentation used in the list of files. Possible answers are (with X
being the number of spaces used for indentation):
space X
tab 8

--separate: analyse each file separately and report results as:
file1: space X
file2: tab 8

--vim-output: output suitable to use inside vim:
set sts=0 | set tabstop=4 | set noexpandtab | set shiftwidth=4

"""

default = ("space", 4 )


class IndentFinder:
	"""
	IndentFinder reports the indentation used in a source file. Its approach is
	not tied to any particular language. It was tested successfully 
	with python, C, C++ and Java code.

	How does it work ?

	It scans each line of the entry file for a space character (white space or
	tab) repeated until a non space character is found. Such a line
	is considered to be a properly indented line of code. Blank lines and
	mixed indentation line are safely ignored. Lines coming after a line
	ending in '\\' have higher chance of being not properly indented, and are
	thus ignored too.
	
	An array stores the number of lines that have a specific indentation: tab,
	number of spaces between 2 and 8. For space indentation, a line is
	considered indented with a base of x if the number of spaces modulo x
	yields zero. Thus, an indentaiton of 4 spaces increases the 2-spaces and
	the 4-spaces indentation line count.

	At the end of the scan phase, the indentation that was used with the
	highest number of lines is taken. For spaces, to avoid the problemes of
	multiples like 2 and 4, the highest indentation number is preferred. A
	lower number is chosen if it reports at least 10% more lines with this
	indentation.

	If IndentFinder ever reports wrong indentation, send me immediately a
	mail, if possible with the offending file.
	"""

	def __init__(self):
		self.clear()

	def parse_file_list( self, file_list ):
		for fname in file_list:
			self.parse_file( fname )

	def parse_file( self, fname ):
		f = open( fname )
		l = f.readline()
		while( l ):
			self.analyse_line( l )
			l = f.readline()
		f.close()

	def clear( self ):
		self.spaces = [ 0, 0, 0, 0, 0, 0, 0 ] # 2-8 entries
		self.tab = 0
		self.nb = 0
		self.indent_re  = re.compile( r"^((\s)\2*)\S" )
		self.skip_line = 0

	def analyse_line( self, line ):
		skip_line = self.skip_line
		if len(line) > 2 and line[-2] == "\\": self.skip_line = 1
		else: self.skip_line = 0
		if skip_line: return

		mo = self.indent_re.match( line )
		if mo:
			self.nb += 1
			if mo.group(2) == '\t':
				self.tab += 1
				return
			nbSpace = len(mo.group(1))
			for i in range( 2, 9 ):
				if (nbSpace % i) == 0:
					self.spaces[i - 2] += 1
			return

	def results( self ):
		if self.tab > max( self.spaces ):
			return ("tab", 8)
		
		nb = 0
		idx = -1
		for i in range(8,1,-1):
			if self.spaces[ i - 2 ] > int( nb * 1.1 ) : # give a 10% threshold
				idx = i
				nb = self.spaces[ idx - 2 ] 

		if idx == -1: # no lines
			raise Exception, "<Empty file>"

		return ("space", idx)

	def __str__ (self):
		try:
			return "%s %d" % self.results()
		except Exception:
			return "<Empty file>"

	def vim_output( self ):
		try:
			ts, n = self.results()
		except Exception:
			return '" Empty file'
		# spaces: 
		# 	=> set sts to the number of spaces
		#   => set tabstop to the number of spaces
		#   => expand tabs to spaces
		#   => set shiftwidth to the number of spaces
		if ts == "space":
			return "set sts=%d | set tabstop=%d | set expandtab | set shiftwidth=%d" % (n,n,n)

		tab_width=4
		# tab:
		#   => set sts to 0
		#   => set expandtab to false
		#   => set shiftwidth to tabstop
		#   tabstop should not be touched.
		if ts == "tab":
			return "set sts=0 | set noexpandtab | set shiftwidth=%d" % tab_width

def main():
	fi = IndentFinder()
	if len(sys.argv) > 1 and sys.argv[1] == "--separate":
		for fname in sys.argv[2:]:
			fi.clear()
			fi.parse_file( fname )
			print "%s : %s" % (fname, str(fi))

	elif len(sys.argv) > 1 and sys.argv[1] == "--vim-output":
		fi.parse_file_list( sys.argv[2:] )
		print fi.vim_output()

	elif len(sys.argv) == 1 or sys.argv[1][0] == "-":
		print help % sys.argv[0]
		return

	else:
		fi.parse_file_list( sys.argv[1:] )
		print str(fi)


if __name__ == "__main__":
	main()
