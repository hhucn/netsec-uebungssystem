from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class StatusHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        laststatus = self.get_argument("laststatus")
        currentstatus = self.get_argument("currentstatus")

        savedstatus = database.getStatus(self.application.config, identifier)

        if not laststatus == savedstatus:
            self.render("status-error", {
                "laststatus": laststatus,
                "currentstatus": currentstatus,
                "identifier": identifier
            })
        else:
            database.setStatus(self.application.config, identifier, currentstatus)
            self.redirect("/detail/%s" % identifier)
