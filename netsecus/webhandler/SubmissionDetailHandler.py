from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission

class SubmissionDetailHandler(NetsecHandler):
    def get(self, submission_id):
        requested_submission = submission.get_from_id(self.application.db, submission_id)
        self.render('submissionDetail', {'submission': requested_submission})
