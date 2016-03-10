from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class TaskDeleteHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id, task_id):
        database = Database(self.application.config)
        database.deleteTask(int(task_id))
        self.redirect("/sheet/%s" % sheet_id)
