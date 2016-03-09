from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class SheetHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        requestedSheet = uri[2:][0]  # remove empty element and "sheet", get sheet number

        sheet = database.getSheetFromID(self.application.config, requestedSheet)

        if sheet:
            self.render('sheet', {'sheet': sheet})
        else:
            logging.error("Specified sheet ('%s') does not exist." % requestedSheet)
            self.redirect("/sheets")
