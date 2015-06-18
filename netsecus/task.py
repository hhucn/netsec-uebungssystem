from __future__ import unicode_literals


class Task(object):

    def __init__(self, number, description, maxPoints, reachedPoints):
        self.number = number
        self.description = description
        self.maxPoints = maxPoints
        self.reachedPoints = reachedPoints
