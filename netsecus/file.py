from __future__ import unicode_literals

import collections
import os

from . import submission

File = collections.namedtuple("File", ["id", "submission_id", "hash", "filename", "size"])


def get_for_submission(db, submission_id):
    db.cursor.execute("""SELECT id, submission_id, hash, filename, size FROM file
                         WHERE submission_id = ?""", (submission_id, ))
    return [File(*row) for row in db.cursor.fetchall()]


def get_from_hash(db, hash):
    db.cursor.execute("SELECT id, submission_id, hash, filename, size FROM file WHERE hash = ?", (hash, ))
    return File(*db.cursor.fetchone())


def get_content_for_hash(db, config, hash):
    requested_file = get_from_hash(db, hash)
    file_submission = submission.get_from_id(db, requested_file.submission_id)
    requested_file_relpath = os.path.join(file_submission.files_path, requested_file.filename)
    requested_file_abspath = os.path.join(config.module_path, requested_file_relpath)

    with open(requested_file_abspath, "rb") as requested_file_handle:
        content = requested_file_handle.read()
        return content
