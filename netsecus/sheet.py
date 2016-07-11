from __future__ import unicode_literals

import collections

Sheet = collections.namedtuple('Sheet', ['id', 'end', 'deleted'])


def get_by_id(db, sheet_id):
    """ Returns the sheet or None if no sheet present """
    db.cursor.execute("SELECT id, end, deleted FROM sheet WHERE id = ?", (sheet_id, ))
    row = db.cursor.fetchone()

    if row:
        return Sheet(*row)
    else:
        return None


def get_all(database):
    database.cursor.execute("SELECT id, end, deleted FROM sheet")
    return [Sheet(*row) for row in database.cursor.fetchall()]


def get_all_total_score(database):
    database.cursor.execute(
        """SELECT
            sheet.id,
            SUM(task.decipoints) AS decipoints
            FROM sheet
            LEFT OUTER JOIN task ON task.sheet_id = sheet.id
            GROUP BY(sheet.id)
        """)
    return [{
        "sheet_id": row[0],
        "decipoints": row[1] if row[1] else 0
    } for row in database.cursor.fetchall()]


def get_all_total_score_by_sheet(database):
    database.cursor.execute(
        """SELECT
            sheet.id,
            SUM(task.decipoints) AS decipoints
            FROM sheet
            LEFT OUTER JOIN task ON task.sheet_id = sheet.id
            GROUP BY(sheet.id)
        """)
    return {row[0]: row[1] if row[1] else 0 for row in database.cursor.fetchall()}


def get_all_total_score_number(database):
    return sum(get_all_total_score_by_sheet(database).values())


def create(database):
    database.cursor.execute("INSERT INTO sheet (end, deleted) VALUES (NULL, 0)")
    database.commit()


def delete(database, sheet_id):
    database.cursor.execute(
        """UPDATE sheet SET deleted = 1 WHERE id = ?""",
        (sheet_id,))
    database.database.commit()


def restore(database, sheet_id):
    database.cursor.execute(
        """UPDATE sheet SET deleted = 0 WHERE id = ?""",
        (sheet_id,))
    database.database.commit()


def edit_end(database, sheet_id, end):
    database.cursor.execute(
        """UPDATE sheet SET end=? WHERE id = ?""",
        (end, sheet_id))
    database.database.commit()
