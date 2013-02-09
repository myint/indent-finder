#!/usr/bin/env python

import unittest

from test_indent_finder import *
from test_many_files import *


def main():
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))

if __name__ == "__main__":
    main()
