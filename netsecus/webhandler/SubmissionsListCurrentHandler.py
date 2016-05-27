from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import student
from .. import grading
from .. import assignment


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all_full(self.application.db)

        current_submission = []

        for sub in submissions:
            found_older_submission_index = -1
            found_correct_student_and_sheet = False

            for index, cursub in enumerate(current_submission):
                if sub["student_id"] == cursub["student_id"] and sub["sheet_id"] == cursub["sheet_id"]:
                    found_correct_student_and_sheet = True
                    if sub["time"] > cursub["time"]:
                        found_older_submission_index = index
                    break

            if not found_correct_student_and_sheet:
                # We found no previous submission from this student for this sheet
                current_submission.append(sub)
            elif found_older_submission_index > -1:
                # We found the student/sheet combination but it is older (based on the timestamp) than the one we are checking for
                current_submission[found_older_submission_index] = sub


        self.render('submissions_list', {'submissions': current_submission, 'heading': "Aktuelle Abgaben"})
