# coding: utf-8
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

    def test_get_header(self):
        self.assertEqual(
            netsecus.helper.get_header({'Subject': 'Abgabe 1'}, 'Subject'),
            'Abgabe 1')
        self.assertEqual(
            netsecus.helper.get_header({
                'Subject': '=?utf-8?Q?Subject=c3=a4?=X=?utf-8?Q?=c3=bc?=',
            }, 'Subject'),
            'SubjectäXü')

    def test_encode_mail_words(self):
        self.assertEqual(netsecus.helper.encode_mail_words(''), '')
        self.assertEqual(netsecus.helper.encode_mail_words('foobar'), 'foobar')
        self.assertEqual(netsecus.helper.encode_mail_words(
            'Philipp Hagemeister <phi-hag@phihag.de>'),
            'Philipp Hagemeister <phi-hag@phihag.de>')
        self.assertEqual(netsecus.helper.encode_mail_words(
            'Philipp Hägemeister <phi-hag@phihag.de>'),
            '=?utf-8?q?Philipp_H=C3=A4?=gemeister <phi-hag@phihag.de>')

tutils.main(__name__)
