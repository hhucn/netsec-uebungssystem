from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        # TODO only list newest submission
        # TODO include correction status
        submissions = submission.get_all(self.application.db)
        self.render('submissions_list_current', {'submissions': submissions})
