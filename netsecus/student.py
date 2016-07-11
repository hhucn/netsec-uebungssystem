from __future__ import unicode_literals

from . import helper
from . import grading

import collections

Student = collections.namedtuple('Student', ['id'])
NamedStudent = collections.namedtuple('Student', ['student', 'aliases'])
FullStudent = collections.namedtuple('FullStudent', ['student', 'aliases', 'submissions'])


def get_full_students(db, where_sql='', filter_params=tuple()):
    from . import submission

    db.cursor.execute('SELECT id FROM student WHERE deleted IS NOT 1' + where_sql, filter_params)
    res = [FullStudent(Student(*row), [], []) for row in db.cursor.fetchall()]
    res_dict = {
        fs.student.id: fs for fs in res
    }

    # Aliases
    db.cursor.execute(
        '''SELECT student.id, alias.alias FROM student, alias
           WHERE student.id = alias.student_id AND student.deleted IS NOT 1''' + where_sql, filter_params)
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
                submission.files_path,
                submission.deleted
            FROM student, submission
           WHERE student.id = submission.student_id AND student.deleted IS NOT 1''' + where_sql, filter_params)
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

    db.cursor.execute("INSERT INTO student (id, primary_alias, deleted) VALUES (null, ?, 0)", (alias, ))
    student = Student(db.cursor.lastrowid)
    db.cursor.execute("INSERT INTO alias (student_id, alias, email) VALUES (?, ?, ?)", (student.id, alias, email))
    db.database.commit()
    return student


def merge(db, main_student_id, merged_student_id):
    from . import submission

    def _get_student_data(student_id):
        db.cursor.execute("""SELECT
            submission.id,
            submission.sheet_id,
            submission.student_id,
            submission.time,
            submission.files_path,
            submission.deleted,
            grading_result.id,
            grading_result.student_id,
            grading_result.sheet_id,
            grading_result.submission_id,
            grading_result.reviews_json,
            grading_result.decipoints,
            grading_result.grader,
            grading_result.sent_mail_uid,
            grading_result.status
            FROM
            submission LEFT OUTER JOIN grading_result on submission.id = grading_result.submission_id
            WHERE submission.student_id = ?""", (student_id,))
        res = []
        SUBMISSION_FIELDS = 6
        for row in db.cursor.fetchall():
            sub = submission.Submission(*row[:SUBMISSION_FIELDS])
            gr = grading.Grading_Result(*row[SUBMISSION_FIELDS:]) if row[SUBMISSION_FIELDS] else None
            res.append((sub, gr))
        return res

    main_d = _get_student_data(main_student_id)
    main_index = {d[0].sheet_id: d for d in main_d}
    merged_d = _get_student_data(merged_student_id)

    for data in merged_d:
        sub, gr = data
        if sub.sheet_id in main_index:
            continue

        new_sub_plan = sub._replace(student_id=main_student_id)
        new_sub = submission.create(db, *new_sub_plan[1:])

        if gr:
            new_gr = gr._replace(student_id=main_student_id, submission_id=new_sub.id)
            db.cursor.execute(
                '''INSERT INTO grading_result
                (student_id, sheet_id, submission_id, reviews_json,
                 decipoints, grader, sent_mail_uid, status)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                ''', new_gr[1:])

    db.cursor.execute(
        """UPDATE submission
           SET deleted = 1
           WHERE student_id = ?""",
        (merged_student_id,))

    db.cursor.execute(
        """UPDATE alias
        SET student_id = ?
        WHERE student_id = ?""",
        (main_student_id, merged_student_id))
    db.cursor.execute(
        """UPDATE student
        SET deleted = 1
        WHERE id = ?""",
        (merged_student_id,))

    db.commit()
