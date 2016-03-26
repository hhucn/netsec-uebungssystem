from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class StudentsHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        students = database.getStudents()
        self.render('students', {'students': students})
