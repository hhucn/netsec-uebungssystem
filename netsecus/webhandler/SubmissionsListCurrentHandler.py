from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import student
from .. import grading


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all_newest(self.application.db)

        subms = [{
            "submission": a_submission,
            "grader": ", ".join(grading.get_all_graders(self.application.db, a_submission.id)),
            "status": grading.get_submission_grade_status(self.application.db, a_submission.id),
            "student": student.get_full_student(self.application.db, a_submission.student_id)
        } for a_submission in submissions]

        for subm in subms:
            if not subm['grader']:
                subm['assigned_grader'] = grading.assign_grader(
                    self.application.config, subm['submission'].id)

        self.render('submissions_list_current', {'submissions': subms})
