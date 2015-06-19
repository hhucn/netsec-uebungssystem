from __future__ import unicode_literals


class Sheet(object):

    def __init__(self, number, tasks, editable):
        self.number = number
        self.tasks = tasks
        self.editable = editable
