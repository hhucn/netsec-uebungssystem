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
        realsubmission = submission.get_full_by_id(self.application.db, submission_id)
        submission_files = file.get_for_submission(self.application.db, realsubmission["id"])
        tasks = task.get_for_sheet(self.application.db, realsubmission["sheet_id"])
        available_graders = grading.get_available_graders(self.application.config)

        total_score = 0
        reached_score = 0
        graded_tasks = []

        for a_task in tasks:
            grading_for_task = grading.get_grade_for_task(self.application.db, a_task.id, realsubmission["id"])
            graded_tasks.append({ "task": a_task, "grading": grading_for_task })
            total_score += a_task.decipoints
            if grading_for_task:
                reached_score += grading_for_task.decipoints

        self.render('submissionDetail', {
            'submission': realsubmission,
            'files': submission_files,
            'grading': graded_tasks,
            'alias': realsubmission["primary_alias"],
            'grader': realsubmission["grader"],
            'available_graders': available_graders,
            'reached_score': reached_score,
            'total_score': total_score
        })
