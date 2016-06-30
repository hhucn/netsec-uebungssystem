from __future__ import unicode_literals

import collections

from . import template_helper

Student = collections.namedtuple('Student', ['id'])
NamedStudent = collections.namedtuple('Student', ['student', 'aliases'])
FullStudent = collections.namedtuple('FullStudent', ['student', 'aliases', 'submissions'])


def get_full_students(db, where_sql='', filter_params=tuple()):
    from . import submission

    db.cursor.execute('SELECT id FROM student WHERE 1' + where_sql, filter_params)
    res = [FullStudent(Student(*row), [], []) for row in db.cursor.fetchall()]
    res_dict = {
        fs.student.id: fs for fs in res
    }

    # Aliases
    db.cursor.execute(
        '''SELECT student.id, alias.alias FROM student, alias
           WHERE student.id = alias.student_id''' + where_sql, filter_params)
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
           WHERE student.id = submission.student_id''' + where_sql, filter_params)
    for row in db.cursor.fetchall():
        student_id = row[0]
        subm = submission.Submission(*row[1:])
        res_dict[student_id].submissions.append(subm)

    return res


def get_full_student(db, student_id):
    fss = get_full_students(db, ' AND student.id = ?', (student_id,))
    if len(fss) != 1:
        raise ValueError('Expected exactly one student')
    return fss[0]


def get_named_student(db, student_id):
    db.cursor.execute(
        '''SELECT alias.alias FROM alias
           WHERE alias.student_id = ?
           ORDER BY alias.id''', (student_id,))
    rows = db.cursor.fetchall()
    if len(rows) != 1:
        raise ValueError('Expected exactly one student')
    return NamedStudent(Student(student_id), [row[0] for row in rows])


def resolve_alias(db, alias):
    """ Fetches or creates the student """

    db.cursor.execute(
        """SELECT student.id FROM alias, student
        WHERE alias.alias = ? AND student.id = alias.student_id""",
        (alias, ))
    res = db.cursor.fetchone()
    if res:
        return Student(res[0])

    db.cursor.execute("INSERT INTO student (id, primary_alias) VALUES (null, ?)", (alias, ))
    student = Student(db.cursor.lastrowid)
    db.cursor.execute("INSERT INTO alias (student_id, alias) VALUES (?, ?)", (student.id, alias))
    db.database.commit()
    return student
