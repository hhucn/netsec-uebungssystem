from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import assignment
from .. import grading
from .. import student
from .. import submission


class OverviewHandler(NetsecHandler):
    def get(self):
        grader = self.request.netsecus_user
        submissions = submission.get_all_newest(self.application.db)
        subms = []

        for a_submission in submissions:
            assigned_grader = assignment.get_for_submission(self.application.db, a_submission.id)
            if assigned_grader and assigned_grader.grader == grader:
                subms.append({
                    "submission": a_submission,
                    "assignment": assigned_grader,
                    "status": grading.get_submission_grade_status(self.application.db, a_submission.id),
                    "student": student.get_full_student(self.application.db, a_submission.student_id),
                })

        self.render('submissions_list_current', {'submissions': subms})
