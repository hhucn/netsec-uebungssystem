from __future__ import unicode_literals

import collections

Grading = collections.namedtuple('Grading', ['id', 'submission_id', 'task_id',
                                 'comment', 'time', 'decipoints', 'grader'])


def get_grade_for_task(db, task_id, submission_id):
    db.cursor.execute(
        """SELECT id, comment, time, decipoints, grader FROM grading WHERE
           submission_id = ? AND task_id = ?""", (submission_id, task_id))
    row = db.cursor.fetchone()
    if row:
        id, comment, time, decipoints, grader = row
        return Grading(id, submission_id, task_id, comment, time, decipoints, grader)


def set_grade_for_task(db, task_id, submission_id, comment, time, decipoints, grader):
    db.cursor.execute("SELECT id FROM grading WHERE submission_id = ? AND task_id = ?", (submission_id, task_id))

    if db.cursor.fetchone():
        # Grading already exists; update
        print(submission_id)
        db.cursor.execute("""UPDATE grading SET comment = ?, time = ?, decipoints = ?, grader = ? WHERE
                             submission_id = ? AND task_id = ?""", (comment, time, decipoints, grader,
                                                                    submission_id, task_id))
    else:
        # Grading does not exist, create
        db.cursor.execute("""INSERT INTO grading (task_id, submission_id, comment, time, decipoints, grader)
                             VALUES(?, ?, ?, ?, ?, ?)""", (task_id, submission_id, comment, time, decipoints, grader))
    db.database.commit()
