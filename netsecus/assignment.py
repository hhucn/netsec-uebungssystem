from __future__ import unicode_literals


def set_for_submission(db, subm, grader):
    db.cursor.execute(
        """SELECT
                id
            FROM grading_result
            WHERE submission_id = ?""", (subm.id,))
    rows = db.cursor.fetchall()

    if rows:
        db.cursor.execute(
            """UPDATE grading_result
                SET grader = ?
                WHERE submission_id = ?""",
            (grader, subm.id)
        )
    else:
        db.cursor.execute(
            """INSERT INTO grading_result
                (student_id, sheet_id, submission_id, reviews_json, decipoints, grader, sent_mail_uid, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                subm.student_id,
                subm.sheet_id,
                subm.id,
                '[]',
                None,
                grader,
                None,
                'assigned'
            )
        )

    db.database.commit()
