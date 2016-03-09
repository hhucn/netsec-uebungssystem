from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class TableHandler(NetsecHandler):
    def get(self):
        sheets = database.getSheets(self.application.config)

        # Count submissions for a sheet
        for sheet in sheets:
            sheetSubmissions = database.getSubmissionForSheet(self.application.config, sheet.id)
            sheet.submissions = len(sheetSubmissions)

            sheetSubmissionsFinished = 0
            for submission in sheetSubmissions:
                if submission.finished:
                    sheetSubmissionsFinished = sheetSubmissionsFinished + 1
            sheet.submissionsFinished = sheetSubmissionsFinished

        self.render("table", {"sheets": sheets})
