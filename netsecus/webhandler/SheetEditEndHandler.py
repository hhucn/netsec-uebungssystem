from __future__ import unicode_literals

from .. import sheet
from .ProtectedPostHandler import ProtectedPostHandler


class SheetEditEndHandler(ProtectedPostHandler):
    def postPassedCSRF(self, sheet_id):
        date = self.get_argument("date")
        sheet.edit_end(self.application.db, sheet_id, date)
        self.redirect("/sheet/%s" % sheet_id)
