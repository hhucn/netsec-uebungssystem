from __future__ import unicode_literals

from .. import student
from .NetsecHandler import NetsecHandler


class StudentHandler(NetsecHandler):
    def get(self, student_id):
        fs = student.get_full_student(self.application.db, student_id)
        self.render('student', {
            'student': fs.student,
            'aliases': fs.aliases,
            'submissions': fs.submissions,
        })
