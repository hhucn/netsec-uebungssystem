from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import student
from .. import grading
from .. import assignment


class SubmissionsListUnfinishedHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all(self.application.db)

        subms = []

        for a_submission in submissions:
            status = grading.get_submission_grade_status(self.application.db, a_submission.id)

            if status != "Fertig":
                subms.append({
                    "submission": a_submission,
                    "assignment": assignment.get_for_submission(self.application.db, a_submission.id),
                    "status": status,
                    "student": student.get_full_student(self.application.db, a_submission.student_id)
                })

        self.render('submissions_list', {'submissions': subms, "heading": "Unbearbeitete Abgaben"})
