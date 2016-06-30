from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import grading
from .. import submission
from .. import task

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

            # TODO: check prev_json here
            prev_decipoints_str = self.get_argument("prev_decipoints_%s" % t.id, default=None)
            prev_decipoints = (
                None
                if (prev_decipoints_str is None or prev_decipoints_str == '')
                else int(prev_decipoints_str)
            )
            prev_comment = self.get_argument("prev_comment_%s" % t.id, default=None)
            prev_time = self.get_argument("prev_time_%s" % t.id, default=None)
            prev_grader = self.get_argument("prev_grader_%s" % t.id, default=None)

            changed = True # TODO: check keys here
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
                    'timestamp': prev_time,
                    'grader': prev_grader,
                }

            reviews.append(review)

        grading.save(
            self.application.db, subm.student_id, subm.sheet_id, submission_id, reviews, grader)

        self.redirect("/submission/%s" % submission_id)
