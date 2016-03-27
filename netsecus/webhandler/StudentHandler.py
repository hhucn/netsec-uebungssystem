from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class StudentHandler(NetsecHandler):
    def get(self, studentID):
        database = Database(self.application.config)
        student = database.getStudent(studentID)
        submissions = database.getSubmissionsForStudent(studentID)
        self.render('student', {'student': student, 'submissions': submissions})
