from __future__ import unicode_literals

import collections

Task = collections.namedtuple("Task", ["id", "sheet_id", "name", "decipoints"])


def get_by_id(database, task_id):
    database.cursor.execute(
        """SELECT id, sheet_id, name, decipoints FROM task
           WHERE id = ?""", (task_id, ))
    row = database.cursor.fetchone()
    if row:
        return Task(*row)
    else:
        return None


def get_for_sheet(database, sheet_id):
    database.cursor.execute("""SELECT id, name, decipoints FROM task WHERE
                               sheet_id = ?""", (sheet_id, ))
    tasks = database.cursor.fetchall()

    result = []

    for task in tasks:
        id, name, decipoints = task
        result.append(Task(id, sheet_id, name, decipoints))

    return result


def create(database, sheet_id, name, decipoints):
    database.cursor.execute("""INSERT INTO task (sheet_id, name, decipoints)
                               VALUES(?,?,?)""", (sheet_id, name, decipoints))
    database.database.commit()


def save(database, task):
    database.cursor.execute(
        "UPDATE task SET name=?, decipoints=? WHERE id=?",
        (task.name, task.decipoints, task.id))
    database.database.commit()

def delete(database, task_id):
    database.cursor.execute("DELETE FROM task WHERE id = ?", (task_id, ))
    database.database.commit()
