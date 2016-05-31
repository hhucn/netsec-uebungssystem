from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListUnfinishedHandler(NetsecHandler):
    def get(self):
        submissions = []

        for sub in submission.get_all_full(self.application.db):
            if sub["status"] != "Fertig":
                submissions.append(sub)

        self.render('submissions_list', {'submissions': submissions, "heading": "Unbearbeitete Abgaben"})
