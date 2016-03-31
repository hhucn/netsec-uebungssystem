from __future__ import unicode_literals

from ..database import Database
from .ProtectedPostHandler import ProtectedPostHandler


class StudentsCreateHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        studentID = self.get_argument("id")
        database = Database(self.application.config)
        database.createStudent(studentID)
        self.redirect("/student/%s" % studentID)
