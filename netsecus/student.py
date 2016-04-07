from __future__ import unicode_literals

import collections

Student = collections.namedtuple('Student', ['id'])

def get_student_aliases(database, student_id):
    database.cursor.execute("SELECT alias FROM alias WHERE student_id = ?", (student_id, ))
    return [row[0] for row in database.cursor.fetchall()]
