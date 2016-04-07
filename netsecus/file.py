from __future__ import unicode_literals


class File(object):

    def __init__(self, fileID, submissionID, sha, filename, path):
        self.id = fileID
        self.submissionID = submissionID
        self.sha = sha
        self.filename = filename
        self.path = path
