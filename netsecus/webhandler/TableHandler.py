from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class TableHandler(NetsecHandler):
    def get(self):
        self.redirect("/sheets")
