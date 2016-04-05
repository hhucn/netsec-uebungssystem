from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SubmissionsHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        students = database.getStudents()
        self.render('submissions', {'students': students})
