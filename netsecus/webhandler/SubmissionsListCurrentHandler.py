from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        current_submission = submission.get_current_full(self.application.db)
        unfinished = 0

        for sub in current_submission:
            if sub.status != "started":
                unfinished = unfinished + 1

        self.render('submissions_list', {
            'submissions': current_submission,
            'heading': "Aktuelle Abgaben",
            'unfinished_corrections_num': unfinished,
            })
