from __future__ import unicode_literals

from .. import sheet

from .ProtectedPostHandler import ProtectedPostHandler


class SheetCreateHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        sheet.create(self.application.db)
        self.redirect("/sheets")
