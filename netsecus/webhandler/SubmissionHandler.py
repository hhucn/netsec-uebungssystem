from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SubmissionHandler(NetsecHandler):
    def get(self, submissionID):
        database = Database(self.application.config)
        files = database.getFilesForSubmission(submissionID)
        submission = database.getSubmissionFromID(submissionID)
        self.render('submission', {'submission': submission, 'files': files})
