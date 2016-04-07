from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler


class TableHandler(NetsecHandler):
    def get(self):
        self.redirect("/sheets")
