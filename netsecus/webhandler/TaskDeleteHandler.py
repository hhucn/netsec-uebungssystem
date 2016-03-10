from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class TaskDeleteHandler(NetsecHandler):
    def post(self, sheet_id, task_id):
        database = Database(self.application.config)
        database.deleteTask(int(task_id))
        self.redirect("/sheet/%s" % sheet_id)
