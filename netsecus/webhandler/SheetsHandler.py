from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler

class SheetsHandler(NetsecHandler):
    def get(self):
        database = Database(self.application.config)
        sheets = database.getSheets()
        self.render('sheets', {'sheets': sheets})
