from __future__ import unicode_literals

import collections

Student = collections.namedtuple('Student', ['id'])

def get_student_aliases(database, student_id):
    database.cursor.execute("SELECT alias FROM alias WHERE student_id = ?", (student_id, ))
    return [row[0] for row in database.cursor.fetchall()]

def resolve_alias(database, alias):
    """ Fetches or creates the student """

    database.cursor.execute(
        """SELECT student.id FROM alias, student
        WHERE alias.alias = ? AND student.id = alias.student_id""",
        (alias, ))
    res = database.cursor.fetchone()
    if res:
        return Student(res[0])

    database.cursor.execute("INSERT INTO student (id) VALUES (null)")
    student = Student(database.cursor.lastrowid)
    database.cursor.execute("INSERT INTO alias (student_id, alias) VALUES (?, ?)", (student.id, alias))
    database.database.commit()
    return student
