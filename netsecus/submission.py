from __future__ import unicode_literals


class Submission(object):

    def __init__(self, submissionID, taskID, identifier, points=0):
        self.id = submissionID
        self.taskID = taskID
        self.identifier = identifier
        self.points = points
