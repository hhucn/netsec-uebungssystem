from __future__ import unicode_literals

import collections

from . import submission

Assignment = collections.namedtuple("Assignment", ["id", "grader", "sheet_id", "student_id"])


def get_for_student_and_sheet(db, student_id, sheet_id):
    db.cursor.execute("""SELECT id, grader, sheet_id, student_id FROM assignment
                         WHERE student_id = ? AND sheet_id = ?""", (student_id, sheet_id))
    row = db.cursor.fetchone()

    if row:
        return Assignment(*row)
    return None


def get_for_submission(db, submission_id):
    subm = submission.get_from_id(db, submission_id)
    return get_for_student_and_sheet(db, subm.student_id, subm.sheet_id)


def get_from_hash(db, hash):
    db.cursor.execute("SELECT id, submission_id, hash, filename, size FROM file WHERE hash = ?", (hash, ))
    return File(*db.cursor.fetchone())


def set_for_student_and_sheet(db, student_id, sheet_id, grader):
    db.cursor.execute("SELECT id FROM assignment WHERE student_id = ? AND sheet_id = ?", (student_id, sheet_id))

    if db.cursor.fetchone():
        # grader already assigned for student and sheet, update
        db.cursor.execute("""UPDATE assignment SET grader = ? WHERE student_id = ? AND sheet_id = ?""",
                          (grader, student_id, sheet_id))
    else:
        # no grader assigned for student and sheet, create
        db.cursor.execute("""INSERT INTO assignment (grader, student_id, sheet_id)
                             VALUES(?, ?, ?)""", (grader, student_id, sheet_id))
    db.database.commit()
