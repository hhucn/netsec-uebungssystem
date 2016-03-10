from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler

class SheetHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        requestedSheet = uri[2:][0]  # remove empty element and "sheet", get sheet number

        database = Database(self.application.config)
        sheet = database.getSheetFromID(requestedSheet)

        if sheet:
            self.render('sheet', {'sheet': sheet})
        else:
            logging.error("Specified sheet ('%s') does not exist." % requestedSheet)
            self.redirect("/sheets")
