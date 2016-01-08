from __future__ import unicode_literals


class Task(object):

    def __init__(self, taskID, sheetID, name, description, maxPoints, reachedPoints=0):
        self.id = taskID
        self.sheetID = sheetID
        self.name = name
        self.description = description
        self.maxPoints = maxPoints
        self.reachedPoints = reachedPoints
