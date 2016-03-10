from __future__ import unicode_literals

from ..database import Database
from .NetsecHandler import NetsecHandler


class PointsHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        sheetNumber = self.get_argument("sheetNumber")
        taskNumber = self.get_argument("taskNumber")
        oldPoints = self.get_argument("oldPoints")
        newPoints = self.get_argument("newPoints")
        database = Database(self.application.config)
        reachedPoints = database.getReachedPoints(sheetNumber, taskNumber, identifier)
        maxPoints = 0

        task = database.getTaskFromSheet(sheetNumber, taskNumber)
        if task:
            maxPoints = task.maxPoints

        if not float(oldPoints) == reachedPoints:
            # Someone submitted new points after this user opened the detail page, but before he could submit his points
            self.render("points", {"redirect": 0, "error": "modified", "oldPoints": oldPoints,
                                   "reachedPoints": reachedPoints, "taskNumber": taskNumber, "sheetNumber": sheetNumber,
                                   "identifier": identifier})
        elif maxPoints < float(newPoints):
            self.render("points", {"redirect": 0, "error": "overMaxPoints", "oldPoints": oldPoints,
                                   "reachedPoints": reachedPoints, "taskNumber": taskNumber, "sheetNumber": sheetNumber,
                                   "identifier": identifier})
        else:
            database.setReachedPoints(sheetNumber, taskNumber, identifier, newPoints)
            self.render("points", {"redirect": 1, "error": "", "oldPoints": oldPoints, "reachedPoints": newPoints,
                        "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})
