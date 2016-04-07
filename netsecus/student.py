from __future__ import unicode_literals

import collections

from . import submission

Student = collections.namedtuple('Student', ['id'])
FullStudent = collections.namedtuple('FullStudent', ['student', 'aliases', 'submissions'])

def get_full_students(db):
    db.cursor.execute('SELECT id FROM student')
    res = [FullStudent(Student(*row), [], []) for row in db.cursor.fetchall()]
    res_dict = {
        fs.student.id: fs for fs in res
    }

    # Aliases
    db.cursor.execute(
        '''SELECT student.id, alias.alias FROM student, alias
           WHERE student.id = alias.student_id''')
    for student_id, alias in db.cursor.fetchall():
        res_dict[student_id].aliases.append(alias)

    # Submissions
    db.cursor.execute(
        '''SELECT
                student.id,
                submission.id,
                submission.sheet_id,
                submission.student_id,
                submission.time,
                submission.files_path
            FROM student, submission
           WHERE student.id = submission.student_id''')
    for row in db.cursor.fetchall():
        student_id = row[0]
        subm = submission.Submission(*row[1:])
        res_dict[student_id].submissions.append(subm)

    return res

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
