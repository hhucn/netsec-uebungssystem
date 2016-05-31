from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListAllHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all_full(self.application.db)

        self.render('submissions_list', {'submissions': submissions, 'heading': "Alle Abgaben"})
