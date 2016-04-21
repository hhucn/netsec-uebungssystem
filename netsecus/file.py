from __future__ import unicode_literals

import collections

File = collections.namedtuple("File", ["id", "submission_id", "hash", "filename", "size"])


def get_for_submission(db, submission_id):
    db.cursor.execute("""SELECT id, submission_id, hash, filename, size FROM file
                         WHERE submission_id = ?""", (submission_id, ))
    return [File(*row) for row in db.cursor.fetchall()]


def get_from_hash(db, hash):
    db.cursor.execute("SELECT id, submission_id, hash, filename, size FROM file WHERE hash = ?", (hash, ))
    return File(*db.cursor.fetchone())
