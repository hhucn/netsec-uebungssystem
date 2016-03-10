from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class SheetCreateHandler(NetsecHandler):
    def post(self):
        name = self.get_argument("name")
        database = Database(self.application.config)
        database.createSheet(name)
        self.redirect("/sheets")
