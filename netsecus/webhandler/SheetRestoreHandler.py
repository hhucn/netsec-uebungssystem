from __future__ import unicode_literals

from .. import sheet
from .ProtectedPostHandler import ProtectedPostHandler


class SheetRestoreHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id):
        sheet.restore(self.application.db, sheet_id)
        self.redirect("/sheets")
