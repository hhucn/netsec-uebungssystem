from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SubmissionsHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        submissions = database.getAllSubmissions()
        self.render('submissions', {'submissions': submissions})
