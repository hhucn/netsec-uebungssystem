from __future__ import unicode_literals

import collections

Task = collections.namedtuple("Task", ["id", "sheet_id", "name", "decipoints"])

def get_by_id(database, task_id):
    database.cursor.execute("""SELECT sheetID, name, maxPoints FROM tasks WHERE
                               taskID = ?""", (id, ))
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
    database.cursor.execute("""INSERT INTO tasks (sheet_id, name, decipoints)
                               VALUES(?,?,?)""", (sheet_id, name, decipoints))
    database.database.commit()

def set_name(database, task_id, name):
    database.cursor.execute("UPDATE task SET name=? WHERE id=?", (name, task_id))
    database.database.commit()

def set_points(database, task_id, decipoints):
    database.cursor.execute("UPDATE task SET decipoints=? WHERE id=?",
                             (decipoints, task_id))
    database.database.commit()

def delete(database, task_id):
    database.cursor.execute("DELETE FROM task WHERE id = ?", (task_id, ))
    database.database.commit()
