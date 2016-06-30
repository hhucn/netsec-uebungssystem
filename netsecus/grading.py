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
                                                           'decipoints', 'grader', 'sent_mail_uid',
                                                           'status'])
# status is one of {'started', 'done'}


def calc_status(reviews):
    all_done = all(r.get('decipoints') is not None for r in reviews)
    return 'done' if all_done else 'started'


def save(db, student_id, sheet_id, submission_id, reviews, grader):
    reviews_json = json.dumps(reviews)
    status = calc_status(reviews)
    decipoints = sum(r['decipoints'] for r in reviews) if status == 'done' else None

    # TODO this should be solved with a view for the newest Grading_Result
    db.cursor.execute(
        """DELETE FROM grading_result
        WHERE student_id = ? AND sheet_id = ?""", (student_id, sheet_id))
    db.cursor.execute(
        """INSERT INTO grading_result
            (student_id, sheet_id, submission_id, reviews_json, decipoints, grader, status)
            VALUES (?, ?, ?, ?, ?, ?, ?);""", (
            student_id, sheet_id, submission_id, reviews_json, decipoints, grader, status))
    db.database.commit()


def get_for_submission(db, submission_id):
    db.cursor.execute(
        """SELECT
                id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid, status
            FROM grading_result
            WHERE submission_id = ?""", (submission_id,))
    rows = db.cursor.fetchall()
    lst = [Grading_Result(*row) for row in rows]
    assert len(lst) <= 1
    if lst:
        return lst[0]
    else:
        return None


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


def on_send_result(db, grading_result_id, sent_mail_uid):
    db.cursor.execute(
        """UPDATE grading_result
        SET sent_mail_uid = ?
        WHERE id = ?""", (sent_mail_uid, grading_result_id))
    db.database.commit()


def unsent_results(db):
    db.cursor.execute(
        """SELECT
            id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid
        FROM grading_result
        WHERE
            sent_mail_uid IS NULL
        ORDER BY grading_result.submission_id ASC, grading_result.id DESC
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
