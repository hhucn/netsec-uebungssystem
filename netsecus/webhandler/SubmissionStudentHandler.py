from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SubmissionStudentHandler(NetsecHandler):
    def get(self, studentID):
        database = Database(self.application.config)
        submissions = database.getSubmissionsForStudent(studentID)
        self.render('submissionStudent', {'submissions': submissions, 'student': studentID})
