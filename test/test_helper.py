from __future__ import unicode_literals

import tutils
import unittest

import netsecus


class TestHelper(unittest.TestCase):
    def test_escape_filename(self):
        self.assertEqual(netsecus.helper.escape_filename('foo123ABZ.bar'), 'foo123ABZ.bar')
        self.assertEqual(netsecus.helper.escape_filename(''), '_')
        self.assertEqual(netsecus.helper.escape_filename('.'), '_')
        self.assertEqual(netsecus.helper.escape_filename('..'), '_.')
        self.assertEqual(netsecus.helper.escape_filename('../a/b/c'), '_._a_b_c')
        self.assertEqual(netsecus.helper.escape_filename('C:ö'), 'C__')
        self.assertEqual(netsecus.helper.escape_filename('foo bar.json'), 'foo bar.json')

tutils.main(__name__)
