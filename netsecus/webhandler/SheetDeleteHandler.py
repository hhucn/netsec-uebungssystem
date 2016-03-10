from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SheetDeleteHandler(NetsecHandler):
    def post(self, sheet_id):
        database = Database(self.application.config)
        database.deleteSheet(sheet_id)
        self.redirect("/sheets")
