from __future__ import unicode_literals


class Sheet(object):

    def __init__(self, sheetID, tasks, editable, timeStart=0, timeEnd=0):
        self.id = sheetID
        self.tasks = tasks
        self.editable = editable
        self.timeStart = timeStart
        self.timeEnd = timeEnd
