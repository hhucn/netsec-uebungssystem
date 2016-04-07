from __future__ import unicode_literals

import collections
import datetime
import os.path
import re
import time

from . import (
    helper,
    sheet,
    student,
)

Submission = collections.namedtuple(
    'Submission',
    ['id', 'sheet_id', 'student_id', 'time', 'files_path'])


def sheet_by_mail(database, message):
    subject = message.get('Subject', '')
    sheet_m = re.match(r'Abgabe\s*(?P<id>[0-9]+)', subject)
    if not sheet_m:
        raise helper.MailError('Invalid subject line, found: %s', subject)
    sheet_id_str = sheet_m.group('id')
    assert re.match(r'^[0-9]+$', sheet_id_str)
    sheet_id = int(sheet_id_str)

    return sheet.get_by_id(database, sheet_id)


def create(database, sheet_id, student_id, timestamp, files_path):
    database.cursor.execute(
        """INSERT INTO submission
            (sheet_id, student_id, time, files_path)
            VALUES (?, ?, ?)""",
            (sheet_id, student_id, timestamp, files_path)
    )
    submission_id = database.cursor.lastrowid
    database.database.commit()
    return Submission(submission_id, sheet_id, student_id, timestamp, files_path)


def handle_mail(config, database, imapmail, message):
    alias = message.get('From', 'anonymous')
    stu = student.resolve_alias(database, alias)
    sheet = sheet_by_mail(database, message)
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

    subm = create(database, sheet.id, stu.id, now_ts, files_path)

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
        with open(payload_path, "wb") as payload_file:
            payload_file.write(payload)

        #database.addFileToSubmission(submission_id, "sha", payload_name, payload_path)

    raise ValueError('would save now - disabled for now')
    commands.move(config, imapmail, mails, "Abgaben")
