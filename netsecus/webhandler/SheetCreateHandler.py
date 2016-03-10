from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class SheetCreateHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        database = Database(self.application.config)
        database.createSheet()
        self.redirect("/sheets")
