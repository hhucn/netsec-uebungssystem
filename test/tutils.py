from __future__ import unicode_literals

import os
import sys
import unittest

import netsecus


def setup_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(root_dir)


def make_db():
    test_config = netsecus.config.Config({}, {
        'database_path': ':memory:',
    })
    return netsecus.database.Database(test_config)


def main(name):
    if name == '__main__':
        unittest.main()
