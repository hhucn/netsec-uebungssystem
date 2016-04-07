from __future__ import unicode_literals

import collections

File = collections.namedtuple("File", ["id", "submission_id", "hash", "filename"])

def get_for_submission(db, submission_id):
    db.cursor.execute("SELECT id, submission_id, hash, filename FROM file WHERE submission_id = ?", (submission_id, ))
    rows = self.cursor.fetchall()
    result = []

    for row in rows:
        result.append(File(*row))

    return result
