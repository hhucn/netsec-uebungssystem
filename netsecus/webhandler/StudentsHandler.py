from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import student


class StudentsHandler(NetsecHandler):
    def get(self):
        full_students = student.get_full_students(self.application.db)
        students_with_scores = []

        for fs in full_students:
            students_with_scores.append({
                "student": fs,
                "score": student.get_student_total_score(self.application.db, fs.student.id)
            })

        self.render('students', {'full_students': students_with_scores})
