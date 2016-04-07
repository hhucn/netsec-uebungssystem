from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler
from .. import task


class SheetsHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        sheets = database.getSheets()
        sheets_tasks = []

        for sheet in sheets:
            tasks_for_sheet = task.get_for_sheet(database, sheet.id)
            if tasks_for_sheet:
                sheets_tasks.append(tasks_for_sheet)

        self.render('sheets', {'sheets_tasks': sheets_tasks, 'sheets': sheets})
