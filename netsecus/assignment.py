from __future__ import unicode_literals

from . import submission


def set_for_student_and_sheet(db, student_id, sheet_id, grader):
    print(grader, student_id, sheet_id)
    db.cursor.execute("""UPDATE grading_result
                         SET grader = ?
                         WHERE student_id = ?
                         AND sheet_id = ?""",
                         (grader, student_id, sheet_id))
    db.database.commit()
