from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        # TODO only list newest submission
        # TODO include correction status
        submissions = submission.get_all(self.application.db)

        subms = [ {"submission": a_submission,
                   "grader": ", ".join(grading.get_all_graders(self.application.db, a_submission.id)),
                   "status": grading.get_submission_grade_status(self.application.db, a_submission.id)}
                 for a_submission in submissions ]


        self.render('submissions_list_current', {'submissions': subms})
