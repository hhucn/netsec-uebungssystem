from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListAllHandler(NetsecHandler):
    def get(self):
        submissions = submission.get_all(self.application.db)
        self.render('submissions_list_all', {'submissions': submissions})
