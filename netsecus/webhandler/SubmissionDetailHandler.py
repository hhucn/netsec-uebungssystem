from __future__ import unicode_literals

import json

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import task
from .. import file
from .. import grading


class SubmissionDetailHandler(NetsecHandler):
    def get(self, submission_id):
        realsubmission = submission.get_full_by_id(self.application.db, submission_id)
        submission_files = file.get_for_submission(self.application.db, realsubmission["id"])
        tasks = task.get_for_sheet(self.application.db, realsubmission["sheet_id"])
        available_graders = grading.get_available_graders(self.application.config)
        gr = grading.get_for_submission(self.application.db, submission_id)

        all_reviews = json.loads(gr.reviews_json) if (gr and gr.reviews_json) else {}
        reviews_by_task = {r['task_id']: r for r in all_reviews}

        total_score = 0
        reached_score = 0
        graded_tasks = []

        for a_task in tasks:
            a_review = reviews_by_task.get(a_task.id)

            graded_tasks.append({
                "task": a_task,
                "review": a_review,
                "review_json": (json.dumps(a_review) if a_review else None),
            })
            total_score += a_task.decipoints
            if a_review and a_review.get('decipoints') is not None:
                reached_score += a_review['decipoints']

        self.render('submissionDetail', {
            'submission': realsubmission,
            'files': submission_files,
            'graded_tasks': graded_tasks,
            'alias': realsubmission["primary_alias"],
            'grader': realsubmission["grader"],
            'available_graders': available_graders,
            'reached_score': reached_score,
            'total_score': total_score
        })
