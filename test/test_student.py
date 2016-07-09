# coding: utf-8
from __future__ import unicode_literals

import collections
import tutils
import unittest

from netsecus import student


Alias = collections.namedtuple('Alias', ['id', 'student_id', 'email'])


def _get_aliases(db):
    db.cursor.execute(
        '''SELECT id, student_id, email FROM alias ORDER BY id ASC''')
    return [Alias(*row) for row in db.cursor.fetchall()]


class TestStudent(unittest.TestCase):
    def test_resolve_alias(self):
        db = tutils.make_db()

        s = student.resolve_alias(db, 'Philipp <philipp@example.org>')
        self.assertEqual(s.id, 1)
        self.assertEqual(_get_aliases(db), [Alias(1, 1, 'philipp@example.org')])

        s = student.resolve_alias(db, 'Philipp <philipp@example.org>')
        self.assertEqual(s.id, 1)
        self.assertEqual(_get_aliases(db), [Alias(1, 1, 'philipp@example.org')])

        s = student.resolve_alias(db, 'Philipp Hagemeister <Philipp@example.org>')
        self.assertEqual(s.id, 1)
        self.assertEqual(_get_aliases(db), [Alias(1, 1, 'philipp@example.org')])

        s = student.resolve_alias(db, 'Tester <Test@example.org>')
        self.assertEqual(s.id, 2)
        self.assertEqual(_get_aliases(db), [
            Alias(1, 1, 'philipp@example.org'),
            Alias(2, 2, 'test@example.org')]
        )


tutils.main(__name__)
