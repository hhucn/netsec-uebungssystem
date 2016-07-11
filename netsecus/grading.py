from __future__ import unicode_literals

import collections
import hashlib
import json

from . import task

Grading_Result = collections.namedtuple('Grading_Result', ['id', 'student_id',
                                                           'sheet_id', 'submission_id', 'reviews_json',
                                                           'decipoints', 'grader', 'sent_mail_uid',
                                                           'status'])
# status is one of {'assigned', 'started', 'done'}


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


def on_send_result(db, grading_result_id, sent_mail_uid):
    db.cursor.execute(
        """UPDATE grading_result
        SET sent_mail_uid = ?
        WHERE id = ?""", (sent_mail_uid, grading_result_id))
    db.database.commit()


def all_results(db, where_filter="status='done'", where_args=[]):
    db.cursor.execute(
        """SELECT
            id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid, status
        FROM grading_result
        WHERE
            1 AND %s
        ORDER BY grading_result.submission_id ASC, grading_result.id DESC
        """ % where_filter, where_args)
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
        'status': status,
    } for (id, student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid, status) in rows]


def unsent_results(db):
    return all_results(db, "sent_mail_uid IS NULL AND status = 'done'")


def get_student_track(db, all_sheet_points, student_id):
    db.cursor.execute(
        """SELECT
            sheet_id, submission_id, decipoints
        FROM grading_result
        WHERE student_id = ? AND status = 'done'
        ORDER BY sheet_id ASC
        """, (student_id,))
    grading_rows = db.cursor.fetchall()

    db.cursor.execute(
        """SELECT
            sheet_id
        FROM submission
        WHERE student_id = ?
        ORDER BY sheet_id ASC
        """, (student_id,))
    sheet_rows = db.cursor.fetchall()
    submitted_sheets = set(sr[0] for sr in sheet_rows)

    res = [{
        'sheet_id': asp['sheet_id'],
        'submitted': asp['sheet_id'] in submitted_sheets,
        'max_decipoints': asp['decipoints'],
    } for asp in all_sheet_points]
    sheet_by_id = {s['sheet_id']: s for s in res}

    for gr in grading_rows:
        sheet_id = gr[0]
        sheet = sheet_by_id[sheet_id]
        sheet['decipoints'] = gr[2]

    return res


def get_student_total_score(db, student_id):
    db.cursor.execute(
        """SELECT
            decipoints
        FROM grading_result
        WHERE student_id = ? AND status = 'done'
        ORDER BY sheet_id ASC
        """, (student_id,))
    decipoint_rows = db.cursor.fetchall()
    return sum(dpr[0] for dpr in decipoint_rows)


def enrich_results(db, grading_results):
    """ Utility function that fetches the various other database objects referenced. """
    # Write in various properties for template
    from . import student

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
