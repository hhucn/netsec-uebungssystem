from __future__ import unicode_literals

import collections

Student = collections.namedtuple('Student', ['id'])


def get_student_aliases(db, student_id):
    db.cursor.execute("SELECT alias FROM alias WHERE student_id = ?", (student_id, ))
    return [row[0] for row in db.cursor.fetchall()]


def resolve_alias(db, alias):
    """ Fetches or creates the student """

    db.cursor.execute(
        """SELECT student.id FROM alias, student
        WHERE alias.alias = ? AND student.id = alias.student_id""",
        (alias, ))
    res = db.cursor.fetchone()
    if res:
        return Student(res[0])

    db.cursor.execute("INSERT INTO student (id) VALUES (null)")
    student = Student(db.cursor.lastrowid)
    db.cursor.execute("INSERT INTO alias (student_id, alias) VALUES (?, ?)", (student.id, alias))
    db.database.commit()
    return student
