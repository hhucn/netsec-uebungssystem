from __future__ import unicode_literals

from .. import task
from .ProtectedPostHandler import ProtectedPostHandler


class TaskDeleteHandler(ProtectedPostHandler):
    def postPassedCSRF(self, task_id):
        t = task.get_by_id(self.application.db, int(task_id))
        task.delete(self.application.db, t.id)
        self.redirect("/sheet/%s" % t.sheet_id)
