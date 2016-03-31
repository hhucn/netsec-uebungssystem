from __future__ import unicode_literals


class Student(object):

    def __init__(self, identifier, alias, deleted=False):
        self.identifier = identifier

        if not alias:
            alias = ""

        self.alias = alias
        self.deleted = deleted
