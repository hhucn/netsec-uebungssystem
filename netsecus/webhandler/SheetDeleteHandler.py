from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class SheetDeleteHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id):
        database = Database(self.application.config)
        database.deleteSheet(sheet_id)
        self.redirect("/sheets")
