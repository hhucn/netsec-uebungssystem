from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import file
from .. import grading


class SubmissionDetailHandler(NetsecHandler):
    def get(self, submission_id):
        requested_submission = submission.get_from_id(self.application.db, submission_id)
        submission_files = file.get_for_submission(self.application.db, requested_submission.id)
        submission_grade = grading.get_grade_for_submission(self.application.db, submission_id)
        self.render('submissionDetail', {'submission': requested_submission, 'files': submission_files,
                                         'grading': submission_grade})
