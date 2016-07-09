from __future__ import unicode_literals

from . import helper
from . import grading

import collections

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

    email = helper.alias2mail(alias)

    db.cursor.execute(
        """SELECT student.id FROM alias, student
        WHERE alias.email = ? AND student.id = alias.student_id""",
        (email, ))
    res = db.cursor.fetchone()
    if res:
        return Student(res[0])

    db.cursor.execute("INSERT INTO student (id, primary_alias) VALUES (null, ?)", (alias, ))
    student = Student(db.cursor.lastrowid)
    db.cursor.execute("INSERT INTO alias (student_id, alias, email) VALUES (?, ?, ?)", (student.id, alias, email))
    db.database.commit()
    return student


def get_student_total_score(db, student_id):
    fs = get_full_student(db, student_id)
    grading_results = grading.unsent_results(db)

    student_total_score = 0

    for subm in fs.submissions:
        for grade in grading_results:
            if grade["student_id"] == int(student_id):
                if grade["sheet_id"] == subm.sheet_id:
                    student_total_score = student_total_score + grade["decipoints"]
                    break

    return student_total_score
