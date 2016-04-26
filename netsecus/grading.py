from __future__ import unicode_literals

import collections
import hashlib
import json

from . import task
from . import student

Grading = collections.namedtuple('Grading', ['id', 'submission_id', 'task_id',
                                 'comment', 'time', 'decipoints', 'grader'])
Grading_Result = collections.namedtuple('Grading_Result', ['id', 'student_id',
                                        'sheet_id', 'submission_id', 'reviews_json',
                                        'decipoints', 'grader', 'sent_mail_uid'])

def get_grade_for_task(db, task_id, submission_id):
    db.cursor.execute(
        """SELECT id, comment, time, decipoints, grader FROM grading WHERE
           submission_id = ? AND task_id = ?""", (submission_id, task_id))
    row = db.cursor.fetchone()
    if not row:
        return None

    id, comment, time, decipoints, grader = row
    return Grading(id, submission_id, task_id, comment, time, decipoints, grader)


def set_grade_for_task(db, task_id, submission_id, comment, time, decipoints, grader):
    db.cursor.execute("SELECT id FROM grading WHERE submission_id = ? AND task_id = ?", (submission_id, task_id))

    if db.cursor.fetchone():
        # Grading already exists; update
        db.cursor.execute("""UPDATE grading SET comment = ?, time = ?, decipoints = ?, grader = ? WHERE
                             submission_id = ? AND task_id = ?""", (comment, time, decipoints, grader,
                                                                    submission_id, task_id))
    else:
        # Grading does not exist, create
        db.cursor.execute("""INSERT INTO grading (task_id, submission_id, comment, time, decipoints, grader)
                             VALUES(?, ?, ?, ?, ?, ?)""", (task_id, submission_id, comment, time, decipoints, grader))
    db.database.commit()


def get_all_graders(db, submission_id):
    db.cursor.execute("SELECT grader FROM grading WHERE submission_id = ?", (submission_id, ))
    rows = db.cursor.fetchall()
    all_graders = []

    for row in rows:
        grader = row[0]
        if grader not in all_graders:
            all_graders.append(grader)

    return all_graders


def get_grades_for_grader(db, grader):
    db.cursor.execute("""SELECT id, student_id, sheet_id, submission_id, reviews_json,
                         decipoints, grader, sent_mail_uid FROM grading_result WHERE grader = ?""", (grader, ))
    rows = db.cursor.fetchall()

    return [ Grading_Result(*row) for row in rows ]


def get_submission_grade_status(db, submission_id):
    db.cursor.execute("SELECT decipoints FROM grading WHERE submission_id = ?", (submission_id, ))
    graded_amount = len(db.cursor.fetchall())

    if graded_amount == 0:
        return "Unbearbeitet"

    task_amount = len(task.get_for_sheet(db, submission_id))

    if task_amount > graded_amount:
        return "Angefangen"

    return "Fertig"


def create_grading_result(db, gr):
    db.cursor.execute(
        """INSERT INTO grading_result
        (student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (
            gr['student_id'],
            gr['sheet_id'],
            gr['submission_id'],
            json.dumps(gr['reviews'], ensure_ascii=False, sort_keys=True),
            gr['decipoints'],
            gr['grader'],
            gr['sent_mail_uid'],
        )
    )


def update_grading_results(db):
    """ This is a temporary workaround until the new data structure is wholly in place.
    A grading result is the result of the (presumably newest) submission of a student for a sheet.
    """

    db.cursor.execute(
        """SELECT
            submission.student_id,
            submission.sheet_id,
            grading.submission_id,
            grading.task_id,
            grading.comment,
            grading.time,
            grading.decipoints,
            grading.grader
        FROM grading, submission
        WHERE
            grading.submission_id = submission.id
        AND grading.submission_id NOT IN (
            SELECT submission_id FROM grading_result
        )
        ORDER BY grading.submission_id DESC, grading.task_id ASC
        """)
    rows = db.cursor.fetchall()

    grs = {}  # key is (student_id, submission_id), value the new object to insert
    for row in rows:
        student_id, sheet_id, submission_id, task_id, comment, timestamp, decipoints, grader = row
        key = (student_id, submission_id)

        if key not in grs:
            grs[key] = {
                'student_id': student_id,
                'sheet_id': sheet_id,
                'submission_id': submission_id,
                'reviews': [],
                'decipoints': 0,
                'grader': grader,
                'sent_mail_uid': None,
            }

        gr = grs[key]
        if gr['submission_id'] != submission_id:
            continue  # this row pertains to a prior submission
        review = {
            'task_id': task_id,
            'comment': comment,
            'timestamp': timestamp,
            'decipoints': decipoints,
            'grader': grader,
        }
        gr['reviews'].append(review)
        gr['decipoints'] += review['decipoints']

    for gr in grs.values():
        create_grading_result(db, gr)

    db.database.commit()


def on_send_result(db, grading_result_id, sent_mail_uid):
    db.cursor.execute(
        """UPDATE grading_result
        SET sent_mail_uid = ?
        WHERE id = ?""", (sent_mail_uid, grading_result_id))
    db.database.commit()


def unsent_results(db):
    update_grading_results(db)

    db.cursor.execute(
        """SELECT
            id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid
        FROM grading_result
        WHERE
            sent_mail_uid IS NULL
        ORDER BY grading_result.submission_id ASC
        """)
    rows = db.cursor.fetchall()

    return [{
        'id': id,
        'student_id': student_id,
        'sheet_id': sheet_id,
        'submission_id': submission_id,
        'reviews': json.loads(reviews_json),
        'decipoints': decipoints,
        'grader': grader,
        'sent_mail_uid': sent_mail_uid,
    } for (id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid) in rows]


def enrich_results(db, grading_results):
    """ Utility function that fetches the various other database objects referenced. """
    # Write in various properties for template
    tasks = task.get_all_dict(db)
    for gr in grading_results:
        for review in gr['reviews']:
            review['task'] = tasks[review['task_id']]
        gr['named_student'] = student.get_named_student(db, gr['student_id'])
        gr['max_decipoints'] = sum(
            review['task'].decipoints
            for review in gr['reviews'])


def get_available_graders(config):
    return sorted(config('korrektoren').keys())


def assign_grader(config, submission_id):
    all_graders = get_available_graders(config)
    rnd = int(
        hashlib.sha512(('%s' % submission_id).encode('ascii')).hexdigest(),
        base=16)
    g_idx = rnd % len(all_graders)
    return all_graders[g_idx]
