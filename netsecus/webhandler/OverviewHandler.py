from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import submission


class OverviewHandler(NetsecHandler):
    def get(self):
        grader = self.request.netsecus_user
        submissions = []

        unfinished = 0

        for sub in submission.get_current_full(self.application.db):
            if sub["grader"] == grader:
                submissions.append(sub)
                if sub.status != "started":
                    unfinished = unfinished + 1

        self.render('submissions_list', {
            'submissions': submissions,
            'heading': "Abgaben für %s" % grader,
            'unfinished_corrections_num': unfinished
            })
