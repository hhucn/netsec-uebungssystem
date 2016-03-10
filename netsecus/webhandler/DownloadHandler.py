from __future__ import unicode_literals

import os

from ..database import Database
from .NetsecHandler import NetsecHandler


class DownloadHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri[len("/download/"):]  # cut away "/download/"

        identifier, sha = uri.split("/")
        database = Database(self.application.config)
        name = database.getFileName(identifier, sha)

        attachmentPath = self.application.config("attachment_path")
        filePath = os.path.join(attachmentPath, identifier, "%s %s" % (sha, name))

        self.set_header("Content-Type", "application/x-octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=" + name)

        with open(filePath, "r") as f:
            self.write(f.read())

        self.finish()
