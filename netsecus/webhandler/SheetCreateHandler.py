from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class SheetCreateHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        name = self.get_argument("name")
        database = Database(self.application.config)
        database.createSheet(name)
        self.redirect("/sheets")
