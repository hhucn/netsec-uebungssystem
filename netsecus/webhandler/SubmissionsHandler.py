from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all(self.application.db)
        self.render('submissions', {'submissions': submissions})
