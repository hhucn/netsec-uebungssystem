from __future__ import unicode_literals


class File(object):

    def __init__(self, fileID, submissionID, sha, filename):
        self.id = fileID
        self.submissionID = submissionID
        self.sha = sha
        self.filename = filename
