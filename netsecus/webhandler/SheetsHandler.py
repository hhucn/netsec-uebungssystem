from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import task
from .. import sheet


class SheetsHandler(NetsecHandler):
    def get(self):
        sheets = sheet.get_all(self.application.db)

        sheets_tasks = (
            task.get_for_sheet(self.application.db, single_sheet.id)
        for single_sheet in sheets)

        self.render('sheets', {'sheets_tasks': sheets_tasks, 'sheets': sheets})
