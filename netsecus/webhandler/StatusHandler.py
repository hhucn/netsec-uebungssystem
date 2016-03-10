from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class StatusHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        laststatus = self.get_argument("laststatus")
        currentstatus = self.get_argument("currentstatus")
        database = Database(self.application.config)
        savedstatus = database.getStatus(identifier)

        if not laststatus == savedstatus:
            self.render("status-error", {
                "laststatus": laststatus,
                "currentstatus": currentstatus,
                "identifier": identifier
            })
        else:
            database.setStatus(identifier, currentstatus)
            self.redirect("/detail/%s" % identifier)
