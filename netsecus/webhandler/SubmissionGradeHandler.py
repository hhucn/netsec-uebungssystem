from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import grading

import datetime
import base64


class SubmissionGradeHandler(ProtectedPostHandler):
    def postPassedCSRF(self, submission_id, task_id):
        comment = self.get_argument("comment")
        decipoints = self.get_argument("points")
        timestamp = datetime.datetime.utcnow()

        receivedAuth = self.request.headers.get("Authorization")
        authMode, auth_b64 = receivedAuth.split(" ")
        auth = base64.b64decode(auth_b64.encode('ascii'))
        username_b, _, password_b = auth.partition(b":")
        grader = username_b.decode('utf-8')

        grading.set_grade_for_task(self.application.db, task_id, submission_id, comment, timestamp, decipoints, grader)
        self.redirect("/submission/%s" % submission_id)
