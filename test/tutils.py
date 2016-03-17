from __future__ import unicode_literals

import os
import sys
import unittest


def setup_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(root_dir)


def main(name):
    if name == '__main__':
        unittest.main()
