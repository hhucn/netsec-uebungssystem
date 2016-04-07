from __future__ import unicode_literals

import collections
import datetime
import hashlib
import itertools
import os.path
import re
import time

from . import (
    commands,
    helper,
    sheet,
    student,
)

Submission = collections.namedtuple(
    'Submission',
    ['id', 'sheet_id', 'student_id', 'time', 'files_path'])


def sheet_by_mail(db, message):
    subject = message.get('Subject', '')
    sheet_m = re.match(r'Abgabe\s*(?P<id>[0-9]+)', subject)
    if not sheet_m:
        raise helper.MailError('Invalid subject line, found: %s', subject)
    sheet_id_str = sheet_m.group('id')
    assert re.match(r'^[0-9]+$', sheet_id_str)
    sheet_id = int(sheet_id_str)

    return sheet.get_by_id(db, sheet_id)


def create(db, sheet_id, student_id, timestamp, files_path):
    db.cursor.execute(
        """INSERT INTO submission
            (sheet_id, student_id, time, files_path)
            VALUES (?, ?, ?, ?)""",
        (sheet_id, student_id, timestamp, files_path)
    )
    submission_id = db.cursor.lastrowid
    db.database.commit()
    return Submission(submission_id, sheet_id, student_id, timestamp, files_path)


def add_file(self, submission_id, hash, filename):
    self.cursor.execute(
        """INSERT INTO file (submission_id, hash, filename)
           VALUES(?, ?, ?)""", (submission_id, hash, filename))
    self.database.commit()


def handle_mail(config, db, imapmail, uid, message):
    alias = message.get('From', 'anonymous')
    stu = student.resolve_alias(db, alias)
    sheet = sheet_by_mail(db, message)
    if not sheet:
        raise ValueError('Cannot find sheet')

    now_ts = time.time()
    now_dt = datetime.datetime.fromtimestamp(now_ts)
    now_str = now_dt.strftime('%Y-%m-%d_%H-%M-%S_%f')

    files_path = os.path.join(
        config("attachment_path"),
        helper.escape_filename(str(stu.id)),
        helper.escape_filename(str(sheet.id)),
        helper.escape_filename(now_str)
    )
    if os.path.exists(files_path):
        orig_files_path = files_path
        for i in itertools.count(2):
            files_path = '%s___%s' % (orig_files_path, i)
            if not os.path.exists(files_path):
                break

    subm = create(db, sheet.id, stu.id, int(now_ts), files_path)

    os.makedirs(files_path)
    for subpart in message.walk():
        fn = subpart.get_filename()
        payload = subpart.get_payload(decode=True)

        if not payload:
            continue

        if not fn:
            fn = 'mail'

        payload_name = helper.escape_filename(fn)
        payload_path = os.path.join(files_path, payload_name)
        hash_str = 'sha256-%s' % hashlib.sha256(payload).hexdigest()
        with open(payload_path, "wb") as payload_file:
            payload_file.write(payload)

        add_file(db, subm.id, hash_str, payload_name)

    commands.move(config, imapmail, uid, "Abgaben")


def get_for_student(db, student_id):
    db.cursor.execute("SELECT id, sheet_id, time, files_path FROM submission WHERE student_id = ?", (student_id,))
    rows = db.cursor.fetchall()
    result = []

    for row in rows:
        result.append(Submission(*row))

    return result


def get_all(db):
    db.cursor.execute("SELECT id, sheet_id, student_id, time, files_path FROM submission")
    rows = db.cursor.fetchall()
    result = []

    for row in rows:
        result.append(Submission(*row))

    return result


def get_from_id(db, submission_id):
    db.cursor.execute("""SELECT id, sheet_id, student_id, time, files_path FROM submission
                         WHERE id = ?""", (submission_id, ))
    return Submission(*db.cursor.fetchone())
