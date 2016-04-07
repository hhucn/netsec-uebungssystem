from __future__ import unicode_literals

import logging

from .NetsecHandler import NetsecHandler
from .. import sheet
from .. import task


class SheetHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        requested_sheet_number = uri[2:][0]  # remove empty element and "sheet", get sheet number

        requested_sheet = sheet.get_by_id(self.application.db, requested_sheet_number)
        tasks_for_sheet = task.get_for_sheet(self.application.db, requested_sheet.id)

        if requested_sheet:
            self.render('sheet', {'sheet': requested_sheet, 'sheet_tasks': tasks_for_sheet})
        else:
            logging.error("Specified sheet ('%s') does not exist." % requested_sheet)
            self.redirect("/sheets")
