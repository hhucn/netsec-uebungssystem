from __future__ import unicode_literals


class Task(object):

    def __init__(self, taskID, sheetID, name, description, maxPoints):
        self.id = taskID
        self.sheetID = sheetID
        self.name = name
        self.description = description
        self.maxPoints = maxPoints
