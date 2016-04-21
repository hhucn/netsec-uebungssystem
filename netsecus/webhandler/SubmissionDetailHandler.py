from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import task
from .. import student
from .. import file
from .. import grading
from .. import assignment


class SubmissionDetailHandler(NetsecHandler):
    def get(self, submission_id):
        requested_submission = submission.get_from_id(self.application.db, submission_id)
        submission_files = file.get_for_submission(self.application.db, requested_submission.id)
        submission_student = student.get_full_student(self.application.db, requested_submission.student_id)
        submission_student_aliases = ", ".join(submission_student.aliases)
        tasks = task.get_for_sheet(self.application.db, requested_submission.sheet_id)
        grader = assignment.get_for_submission(self.application.db, submission_id)
        graded_tasks = []

        for a_task in tasks:
            graded_tasks.append({"task": a_task,
                                 "grading": grading.get_grade_for_task(self.application.db, a_task.id,
                                                                       requested_submission.id)})

        self.render('submissionDetail', {'submission': requested_submission, 'files': submission_files,
                                         'grading': graded_tasks, 'aliases': submission_student_aliases,
                                         'grader': grader})
