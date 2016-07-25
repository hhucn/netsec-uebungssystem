from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListAllHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all_full(self.application.db)

        unfinished = 0

        for sub in submissions:
            if sub.status != "started":
                unfinished = unfinished + 1

        self.render('submissions_list', {
            'submissions': submissions,
            'heading': "Alle Abgaben",
            'unfinished_corrections_num': unfinished,
            })
