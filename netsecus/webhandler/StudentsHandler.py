from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import student


class StudentsHandler(NetsecHandler):
    def get(self):
        full_students = student.get_full_students(self.application.db)
        self.render('students', {'full_students': full_students})
