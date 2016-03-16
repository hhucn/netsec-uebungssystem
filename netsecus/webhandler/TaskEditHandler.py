from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class TaskEditHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id, task_id):
        database = Database(self.application.config)
        name = self.get_argument("name")
        points = self.get_argument("points")
        database.setNameForTask(task_id, name)
        database.setPointsForTask(task_id, points)
        self.redirect("/sheet/%s" % sheet_id)
