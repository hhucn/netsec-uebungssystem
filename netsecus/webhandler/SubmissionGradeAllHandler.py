from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import grading
from .. import submission
from .. import task

import json
import time


class SubmissionGradeAllHandler(ProtectedPostHandler):
    def postPassedCSRF(self, submission_id):
        subm = submission.get_from_id(self.application.db, submission_id)
        tasks = task.get_for_sheet(self.application.db, subm.sheet_id)

        grader = self.request.netsecus_user
        assert grader

        reviews = []
        now = time.time()
        for t in tasks:
            decipoints_str = self.get_argument("points_%s" % t.id)
            decipoints = int(round(float(decipoints_str) * 10)) if decipoints_str else None
            comment = self.get_argument("comment_%s" % t.id)

            # Check whether anything has changed
            prev_json = self.get_argument("prev_json_%s" % t.id, default=None)
            prev = (json.loads(prev_json) if prev_json else {})
            changed = (
                prev.get('decipoints') != decipoints or
                prev.get('comment') != comment
            )

            if changed:
                review = {
                    'task_id': t.id,
                    'comment': comment,
                    'decipoints': decipoints,
                    'timestamp': now,
                    'grader': grader,
                }
            else:
                review = {
                    'task_id': t.id,
                    'comment': comment,
                    'decipoints': decipoints,
                    'timestamp': prev.get('time'),
                    'grader': prev.get('grader'),
                }

            reviews.append(review)

        grading.save(
            self.application.db, subm.student_id, subm.sheet_id, submission_id, reviews, grader)

        self.redirect("/submission/%s" % submission_id)
