from __future__ import unicode_literals

import collections
import hashlib

from . import task

Grading = collections.namedtuple('Grading', ['id', 'submission_id', 'task_id',
                                 'comment', 'time', 'decipoints', 'grader'])


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


def get_submission_grade_status(db, submission_id):
    db.cursor.execute("SELECT decipoints FROM grading WHERE submission_id = ?", (submission_id, ))
    graded_amount = len(db.cursor.fetchall())

    if graded_amount == 0:
        return "Unbearbeitet"

    task_amount = len(task.get_for_sheet(db, submission_id))

    if task_amount > graded_amount:
        return "Angefangen"

    return "Fertig"


def get_available_graders(config):
    return list(config('korrektoren').keys())


def assign_grader(config, submission_id):
    all_graders = get_available_graders(config)
    rnd = int(
        hashlib.sha512(('%s' % submission_id).encode('ascii')).hexdigest(),
        base=16)
    g_idx = rnd % len(all_graders)
    return all_graders[g_idx]
