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
    database.cursor.execute("""SELECT
                               sheet.id,
                               task.id,
                               task.decipoints
                               FROM sheet
                               LEFT OUTER JOIN task
                               ON task.sheet_id = sheet.id
                               """)
    return [
        {
            "sheet_id": row[0],
            "task_id": row[1],
            "decipoints": row[2] if row[2] else 0
        } for row in database.cursor.fetchall()]


def get_all_total_score_number(database):
    total_score = 0

    for sheet_task in get_all_total_score(database):
        total_score += sheet_task["decipoints"]

    return total_score


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
