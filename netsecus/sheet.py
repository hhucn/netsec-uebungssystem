from __future__ import unicode_literals


class Sheet(object):

    def __init__(self, sheetID, tasks, timeEnd=0, deleted=False):
        self.id = sheetID
        self.tasks = tasks
        self.timeEnd = timeEnd
        self.deleted = deleted
