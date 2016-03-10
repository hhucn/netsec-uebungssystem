from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class PointsHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        sheetNumber = self.get_argument("sheetNumber")
        taskNumber = self.get_argument("taskNumber")
        newPoints = self.get_argument("newPoints")
        database = Database(self.application.config)
        reachedPoints = database.getReachedPoints(sheetNumber, taskNumber, identifier)
        points = 0

        task = database.getTaskFromSheet(sheetNumber, taskNumber)
        if task:
            points = task.points

        if points < float(newPoints):
            self.render("points", {"redirect": 0, "error": "overMaxPoints", "reachedPoints": reachedPoints,
                                   "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})
        else:
            database.setReachedPoints(sheetNumber, taskNumber, identifier, newPoints)
            self.render("points", {"redirect": 1, "error": "", "reachedPoints": newPoints, "taskNumber": taskNumber,
                        "sheetNumber": sheetNumber, "identifier": identifier})
