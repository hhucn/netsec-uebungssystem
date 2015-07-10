from __future__ import unicode_literals


class Task(object):

    def __init__(self, taskID, name, description, maxPoints, reachedPoints):
        self.id = taskID
        self.name = name
        self.description = description
        self.maxPoints = maxPoints
        self.reachedPoints = reachedPoints
