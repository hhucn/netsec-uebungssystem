from __future__ import unicode_literals

from .. import grading
from .. import sheet
from .. import student

from .NetsecHandler import NetsecHandler
from .ProtectedPostHandler import ProtectedPostHandler


class MergeSelectHandler(NetsecHandler):
    def get(self, student_id_str):
        all_students = student.get_studentname_info(self.application.db)
        student_id = int(student_id_str)
        merged_Student = next(s for s in all_students if s['id'] == student_id)
        other_students = sorted(
            (s for s in all_students if s['id'] != student_id),
            key=lambda s: s['primary_alias'])

        self.render('merge_select', {
            'merged_student': merged_Student,
            'other_students': other_students,
        })


class MergePreviewHandler(NetsecHandler):
    def get(self, merged_student_id_str):
        main_student_id = int(self.get_argument('main_id'))
        merged_student_id = int(merged_student_id_str)

        all_sheet_points = sheet.get_all_total_score(self.db)
        main_student = student.get_full_student(self.db, main_student_id)
        merged_student = student.get_full_student(self.db, merged_student_id)

        main_track = grading.get_student_track(self.db, all_sheet_points, main_student_id)
        merged_track = grading.get_student_track(self.db, all_sheet_points, merged_student_id)

        self.render('merge_preview', {
            'main_student': main_student,
            'merged_student': merged_student,
            'main_track': main_track,
            'merged_track': merged_track,
        })


class MergeHandler(ProtectedPostHandler):
    def postPassedCSRF(self, merged_student_id_str):
        main_student_id = int(self.get_argument('main_id'))
        merged_student_id = int(merged_student_id_str)

        student.merge(self.db, main_student_id, merged_student_id)

        self.redirect('/student/%d' % main_student_id)
