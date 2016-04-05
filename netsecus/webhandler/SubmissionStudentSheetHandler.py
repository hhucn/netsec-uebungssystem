from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SubmissionStudentSheetHandler(NetsecHandler):
    def get(self, studentID, sheetID):
        database = Database(self.application.config)
        submissions = database.getSubmissionsForStudent(studentID)
        files = []

        for submission in submissions:
            files.append(database.getFilesForSubmission(submission.id))

        self.render('submissionStudentSheet', {'files': files, 'student': studentID, 'sheet': sheetID})
