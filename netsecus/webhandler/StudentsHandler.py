from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import grading
from .. import sheet
from .. import student


class StudentsHandler(NetsecHandler):
    def get(self):
        full_students = student.get_full_students(self.application.db)
        students_with_scores = []

        for fs in full_students:
            students_with_scores.append({
                "student": fs,
                "score": grading.get_student_total_score(self.application.db, fs.student.id)
            })

        total_score = sheet.get_all_total_score_number(self.application.db)

        self.render('students', {
            'full_students': students_with_scores,
            'total_score': total_score,
        })
