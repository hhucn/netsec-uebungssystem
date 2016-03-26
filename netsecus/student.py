from __future__ import unicode_literals


class Student(object):

    def __init__(self, identifier, alias):
        self.identifier = identifier

        if not isinstance(alias, list):
            alias = [alias]
        self.alias = alias
