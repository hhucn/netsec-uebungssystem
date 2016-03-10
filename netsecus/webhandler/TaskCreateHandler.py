from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class TaskCreateHandler(NetsecHandler):
    def post(self, sheet_id):
        name = self.get_argument("name")
        points = self.get_argument("points")
        database = Database(self.application.config)
        database.createTask(sheet_id, name, points)
        self.redirect("/sheet/%s" % sheet_id)
