from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import grading

import datetime


class SubmissionGradeHandler(ProtectedPostHandler):
    def postPassedCSRF(self, submission_id, task_id):
        comment = self.get_argument("comment")
        decipoints = self.get_argument("points")
        timestamp = datetime.datetime.utcnow()
        grader = self.request.netsecus_user

        grading.set_grade_for_task(self.application.db, task_id, submission_id, comment, timestamp, decipoints, grader)
        self.redirect("/submission/%s" % submission_id)
