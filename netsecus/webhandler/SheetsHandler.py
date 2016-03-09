from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class SheetsHandler(NetsecHandler):
    def get(self):
        sheets = database.getSheets(self.application.config)
        self.render('sheets', {'sheets': sheets})
