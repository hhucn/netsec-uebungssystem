# coding: utf-8
from __future__ import unicode_literals

import collections
import tutils
import unittest

from netsecus import (
    grading,
    student,
    submission,
)


Alias = collections.namedtuple('Alias', ['id', 'student_id', 'email'])


def _get_aliases(db):
    db.cursor.execute(
        '''SELECT id, student_id, email FROM alias ORDER BY id ASC''')
    return [Alias(*row) for row in db.cursor.fetchall()]


def _testable_subs(subs):
    return sorted(map(tutils.remove_id, subs), key=lambda sub: sub.time)


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

    def test_merge(self):
        def _grade(sub, decipoints):
            return grading.save(db, sub.student_id, sub.sheet_id, sub.id, [{'decipoints': decipoints}], 'philipp')

        all_sheet_points = [{
            'sheet_id': sheet_id,
            'decipoints': 10 * points,
        } for sheet_id, points in enumerate([21, 22, 23, 24, 25, 26], start=1)]

        db = tutils.make_db()
        s = student.resolve_alias(db, 'Philipp <philipp@uni-duesseldorf.de>')
        self.assertEqual(s.id, 1)
        s2 = student.resolve_alias(db, 'Philipp <philipp@private.com>')
        self.assertEqual(s2.id, 2)
        studs = student.get_full_students(db)
        self.assertEqual(len(studs), 2)
        self.assertEqual(_get_aliases(db), [
            Alias(1, 1, 'philipp@uni-duesseldorf.de'),
            Alias(2, 2, 'philipp@private.com'),
        ])

        sub = submission.create(db, 1, s.id, 1000, '')
        _grade(sub, 11)

        sub = submission.create(db, 2, s2.id, 1001, '')
        _grade(sub, 12)

        sub = submission.create(db, 2, s2.id, 1002, '')
        _grade(sub, 13)

        sub = submission.create(db, 3, s2.id, 1003, '')
        _grade(sub, 14)

        sub = submission.create(db, 4, s.id, 1004, '')
        _grade(sub, 15)

        sub = submission.create(db, 4, s2.id, 1005, '')
        _grade(sub, 16)

        subs = _testable_subs(submission.get_all(db))
        self.assertEqual(subs, [
            submission.Submission(id=None, sheet_id=1, student_id=1, time=1000, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=2, student_id=2, time=1001, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=2, student_id=2, time=1002, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=3, student_id=2, time=1003, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=4, student_id=1, time=1004, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=4, student_id=2, time=1005, files_path='', deleted=0),
        ])
        grs = grading.get_student_track(db, all_sheet_points, s.id)
        self.assertEqual(grs, [
            {'sheet_id': 1, 'max_decipoints': 210, 'submitted': True, 'decipoints': 11},
            {'sheet_id': 2, 'max_decipoints': 220, 'submitted': False},
            {'sheet_id': 3, 'max_decipoints': 230, 'submitted': False},
            {'sheet_id': 4, 'max_decipoints': 240, 'submitted': True, 'decipoints': 15},
            {'sheet_id': 5, 'max_decipoints': 250, 'submitted': False},
            {'sheet_id': 6, 'max_decipoints': 260, 'submitted': False},
        ])
        grs = grading.get_student_track(db, all_sheet_points, s2.id)
        self.assertEqual(grs, [
            {'sheet_id': 1, 'max_decipoints': 210, 'submitted': False},
            {'sheet_id': 2, 'max_decipoints': 220, 'submitted': True, 'decipoints': 13},
            {'sheet_id': 3, 'max_decipoints': 230, 'submitted': True, 'decipoints': 14},
            {'sheet_id': 4, 'max_decipoints': 240, 'submitted': True, 'decipoints': 16},
            {'sheet_id': 5, 'max_decipoints': 250, 'submitted': False},
            {'sheet_id': 6, 'max_decipoints': 260, 'submitted': False},
        ])

        # Run the actual merge - this is the line we're testing
        student.merge(db, s.id, s2.id)

        studs = student.get_full_students(db)
        self.assertEqual(len(studs), 1)
        self.assertEqual(_get_aliases(db), [
            Alias(1, 1, 'philipp@uni-duesseldorf.de'),
            Alias(2, 1, 'philipp@private.com'),
        ])

        subs = _testable_subs(submission.get_all(db))
        self.assertEqual(subs, [
            submission.Submission(id=None, sheet_id=1, student_id=1, time=1000, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=2, student_id=1, time=1001, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=2, student_id=1, time=1002, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=3, student_id=1, time=1003, files_path='', deleted=0),
            submission.Submission(id=None, sheet_id=4, student_id=1, time=1004, files_path='', deleted=0),
        ])

        grs = grading.get_student_track(db, all_sheet_points, s.id)
        self.assertEqual(grs, [
            {'sheet_id': 1, 'max_decipoints': 210, 'submitted': True, 'decipoints': 11},
            {'sheet_id': 2, 'max_decipoints': 220, 'submitted': True, 'decipoints': 13},
            {'sheet_id': 3, 'max_decipoints': 230, 'submitted': True, 'decipoints': 14},
            {'sheet_id': 4, 'max_decipoints': 240, 'submitted': True, 'decipoints': 15},
            {'sheet_id': 5, 'max_decipoints': 250, 'submitted': False},
            {'sheet_id': 6, 'max_decipoints': 260, 'submitted': False},
        ])


tutils.main(__name__)
