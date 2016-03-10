from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler

class TableHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        sheets = database.getSheets()

        # Count submissions for a sheet
        for sheet in sheets:
            sheetSubmissions = database.getSubmissionForSheet(sheet.id)
            sheet.submissions = len(sheetSubmissions)

            sheetSubmissionsFinished = 0
            for submission in sheetSubmissions:
                if submission.finished:
                    sheetSubmissionsFinished = sheetSubmissionsFinished + 1
            sheet.submissionsFinished = sheetSubmissionsFinished

        self.render("table", {"sheets": sheets})
