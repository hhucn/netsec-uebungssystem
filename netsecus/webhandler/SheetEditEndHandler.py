from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class SheetEditEndHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id):
        database = Database(self.application.config)
        date = self.get_argument("date")
        database.editEnd(sheet_id, date)
        self.redirect("/sheet/%s" % sheet_id)
