from __future__ import unicode_literals

from .. import task

from .ProtectedPostHandler import ProtectedPostHandler


class TaskCreateHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id_str):
        sheet_id = int(sheet_id_str)
        name = self.get_argument("name")
        points = self.get_argument("points")
        decipoints = int(float(points) * 10)
        task.create(self.application.db, sheet_id, name, decipoints)
        self.redirect("/sheet/%s" % sheet_id)
