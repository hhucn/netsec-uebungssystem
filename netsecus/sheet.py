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

def create(db):
    db.cursor.execute("INSERT INTO sheet (end, deleted) VALUES (NULL, 0)")
    db.commit()
