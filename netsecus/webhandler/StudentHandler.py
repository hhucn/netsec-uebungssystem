from __future__ import unicode_literals

from .. import grading
from .. import sheet
from .. import student
from .NetsecHandler import NetsecHandler


class StudentHandler(NetsecHandler):
    def get(self, student_id):
        fs = student.get_full_student(self.application.db, student_id)

        grading_results = grading.unsent_results(self.application.db)

        all_sheet_points = sheet.get_all_total_score(self.application.db)
        for gr in grading_results:
            gr['student_track'] = grading.get_student_track(self.application.db, all_sheet_points, gr['student_id'])
            gr['total_decipoints'] = sum(st.get('decipoints', 0) for st in gr['student_track'])

        submission_with_score = []
        student_total_score = 0
        reachable_total_score = 0

        for subm in fs.submissions:
            student_score = 0

            for grade in grading_results:
                if grade["student_id"] == int(student_id):
                    if grade["sheet_id"] == subm.sheet_id:
                        student_score = grade["decipoints"]
                        total_score = grade["total_decipoints"]
                        break

            submission_with_score.append(
                {
                    "submission": subm,
                    "student_score": student_score,
                    "total_score": total_score
                }
            )

            student_total_score = student_total_score + student_score

        self.render('student', {
            'student': fs.student,
            'aliases': fs.aliases,
            'submissions': submission_with_score,
            'student_total_score': student_total_score,
            'reachable_total_score': total_score
        })
