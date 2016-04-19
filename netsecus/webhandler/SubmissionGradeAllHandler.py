from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import grading
from .. import submission
from .. import task

import datetime


class SubmissionGradeAllHandler(ProtectedPostHandler):
    def postPassedCSRF(self, submission_id):
        subm = submission.get_from_id(self.application.db, submission_id)
        tasks = task.get_for_sheet(self.application.db, subm.sheet_id)

        timestamp = datetime.datetime.utcnow()
        grader = self.request.netsecus_user
        assert grader
        print('grader: %r' % grader)

        for t in tasks:
            comment = self.get_argument("comment_%s" % t.id)
            decipoints = self.get_argument("points_%s" % t.id)

            grading.set_grade_for_task(
                self.application.db, t.id, submission_id,
                comment, timestamp, decipoints, grader)

        self.redirect("/submission/%s" % submission_id)
