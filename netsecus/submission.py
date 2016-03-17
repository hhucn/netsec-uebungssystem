from __future__ import unicode_literals


class Submission(object):

    def __init__(self, submissionID, sheetID, identifier, points=0):
        self.id = submissionID
        self.sheetID = sheetID
        self.identifier = identifier
        self.points = points
