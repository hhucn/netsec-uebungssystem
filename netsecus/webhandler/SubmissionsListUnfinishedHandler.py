from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListUnfinishedHandler(NetsecHandler):
    def get(self):
        submissions = []

        for sub in submission.get_all_full(self.application.db):
            if sub["status"] != "Fertig" or sub["status"] != "done":
                submissions.append(sub)

        self.render('submissions_list', {
            'submissions': submissions,
            'heading': 'Unbearbeitete Abgaben',
            'unfinished_corrections_num': 0,
            'show_unfinished_corrections': False,
            })
