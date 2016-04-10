from __future__ import unicode_literals

import collections

Grading = collections.namedtuple('Grading', ['id', 'submission_id', 'comment', 'time', 'decipoints', 'grader'])

def get_grade_for_submission(db, submission_id):
    db.cursor.execute(
        """SELECT id, comment, time, decipoints, grader FROM grading WHERE submission_id = ?""", (submission_id, ))
    row = db.cursor.fetchone()
    if row:
        id, comment, time, decipoints, grader = row
        return Grading(id, submission_id, comment, time, decipoints, grader)


def set_grade_for_submission(db, submission_id, comment, time, decipoints, grader):
    db.cursor.execute("SELECT id FROM grading WHERE submission_id = ?", (submission_id, ))

    if db.cursor.fetchone():
        # Grading already exists; update
        print(submission_id)
        db.cursor.execute("""UPDATE grading SET comment = ?, time = ?, decipoints = ?, grader = ? WHERE
                             submission_id = ?""", (comment, time, decipoints, grader, submission_id))
    else:
        # Grading does not exist, create
        db.cursor.execute("""INSERT INTO grading (submission_id, comment, time, decipoints, grader)
                             VALUES(?, ?, ?, ?, ?)""", (submission_id, comment, time, decipoints, grader))
    db.database.commit()
