from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class TaskDeleteHandler(NetsecHandler):
    def post(self, sheet_id, task_id):
        database.deleteTask(self.application.config, int(task_id))
        self.redirect("/sheet/%s" % sheet_id)
