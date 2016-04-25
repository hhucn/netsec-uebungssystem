from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import student


class SubmissionsListAllHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all(self.application.db)

        subms = [{
            "submission": a_submission,
            "student": student.get_full_student(self.application.db, a_submission.student_id),
        } for a_submission in submissions]

        self.render('submissions_list_all', {'submissions': subms})
