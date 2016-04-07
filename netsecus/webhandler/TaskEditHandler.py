from __future__ import unicode_literals

from .. import task
from .ProtectedPostHandler import ProtectedPostHandler


class TaskEditHandler(ProtectedPostHandler):
    def postPassedCSRF(self, task_id):
        t = task.get_by_id(self.application.db, int(task_id))
        decipoints = int(float(self.get_argument("points")) * 10)
        tnew = t._replace(
            name=self.get_argument("name"),
            decipoints=decipoints,
        )
        task.save(self.application.db, tnew)

        self.redirect("/sheet/%s" % tnew.sheet_id)
