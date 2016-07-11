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
    sendmail,
)

Submission = collections.namedtuple(
    'Submission',
    ['id', 'sheet_id', 'student_id', 'time', 'files_path', 'deleted'])


def _match_subject(subject):
    return re.match(r'^Abgabe\s*(?P<id>[0-9]+)', subject)


def sheet_by_mail(db, uid, message):
    subject = helper.get_header(message, 'Subject', '')
    sheet_m = _match_subject(subject)
    if not sheet_m:
        raise helper.MailError(uid, 'Invalid subject line, found: %s' % subject)
    sheet_id_str = sheet_m.group('id')
    assert re.match(r'^[0-9]+$', sheet_id_str)
    sheet_id = int(sheet_id_str)

    res = sheet.get_by_id(db, sheet_id)
    if not res:
        raise helper.MailError(uid, 'Could not find a sheet with id %s' % sheet_id)
    return res


def create(db, sheet_id, student_id, timestamp, files_path, deleted=0):
    db.cursor.execute(
        """INSERT INTO submission
            (sheet_id, student_id, time, files_path, deleted)
            VALUES (?, ?, ?, ?, ?)""",
        (sheet_id, student_id, timestamp, files_path, deleted)
    )
    submission_id = db.cursor.lastrowid
    db.database.commit()
    return Submission(submission_id, sheet_id, student_id, timestamp, files_path, 0)


def add_file(self, submission_id, hash, filename, size):
    self.cursor.execute(
        """INSERT INTO file (submission_id, hash, filename, size)
           VALUES(?, ?, ?, ?)""", (submission_id, hash, filename, size))
    self.database.commit()


def handle_mail(config, db, imapmail, uid, message):
    subject = helper.get_header(message, 'Subject', '(none)')
    if not _match_subject(subject):
        return  # Interactive mail, we don't care about those

    alias = message.get('From', 'anonymous')
    try:
        stu = student.resolve_alias(db, alias)
        sheet = sheet_by_mail(db, uid, message)

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

        mailtext = b""

        os.makedirs(files_path)
        for subpart in message.walk():
            fn = subpart.get_filename()
            payload = subpart.get_payload(decode=True)

            if not payload:
                continue

            if fn:
                # file part
                payload_name = helper.escape_filename(fn)
                payload_path = os.path.join(files_path, payload_name)
                payload_size = len(payload)
                hash_str = 'sha256-%s' % hashlib.sha256(payload).hexdigest()
                with open(payload_path, "wb") as payload_file:
                    payload_file.write(payload)

                add_file(db, subm.id, hash_str, payload_name, payload_size)
            else:
                # message part
                if mailtext:
                    mailtext += b"\n\n--- Part ---\n"
                mailtext += payload

        if mailtext:
            # write "mail" file
            payload_path = os.path.join(files_path, "mail")
            payload_size = len(mailtext)
            hash_str = 'sha256-%s' % hashlib.sha256(mailtext).hexdigest()
            with open(payload_path, "wb") as payload_file:
                payload_file.write(mailtext)

            add_file(db, subm.id, hash_str, "mail", payload_size)

        commands.move(config, imapmail, uid, "Abgaben")

        sendmail.send_template(config, alias, "Mail erhalten: %s" % subject, "mail_received.html")
    except helper.MailError as me:
        sendmail.send_template(config, alias, "Mail fehlerhaft: %s" % subject, "mail_sheet_not_found.html")
        raise me


def get_for_student(db, student_id):
    db.cursor.execute(
        """SELECT id, sheet_id, student_id, time, files_path, deleted
           FROM submission WHERE student_id = ?""", (student_id,))
    rows = db.cursor.fetchall()
    return [Submission(*row) for row in rows]


def get_all(db):
    db.cursor.execute(
        """SELECT id, sheet_id, student_id, time, files_path, deleted
           FROM submission WHERE deleted IS NOT 1""")
    rows = db.cursor.fetchall()
    return [Submission(*row) for row in rows]


def get_full_by_id(db, id):
    return get_full_sql(db, "submission.id = %s" % id)[0]


def get_all_full(db):
    return get_full_sql(db, "")


def get_full_sql(db, filter):
    db.cursor.execute("""SELECT
                         submission.id,
                         submission.sheet_id,
                         submission.student_id,
                         submission.time,
                         submission.files_path,
                         student.primary_alias,
                         grading_result.grader,
                         grading_result.decipoints,
                         grading_result.status
                         FROM
                         submission
                         INNER JOIN student ON
                         submission.student_id = student.id
                         AND student.deleted IS NOT 1
                         AND submission.deleted IS NOT 1
                         %s
                         LEFT OUTER JOIN grading_result ON
                         submission.id = grading_result.submission_id
                         ORDER BY submission.id DESC
                         """ %
                      (" AND %s" % filter if filter else ""))
    rows = db.cursor.fetchall()

    all_full = []

    for row in rows:
        id, sheet_id, student_id, time, files_path, primary_alias, grader, decipoints, status = row
        all_full.append({
            "id": id,
            "sheet_id": sheet_id,
            "student_id": student_id,
            "time": time,
            "files_path": files_path,
            "primary_alias": primary_alias,
            "grader": grader,
            "decipoints": decipoints,
            "status": status if status else "Unbearbeitet"
        })

    return all_full


def get_current_full(db):
    current_submission = []

    for sub in get_all_full(db):
        found_older_submission_index = -1
        found_correct_student_and_sheet = False

        for index, cursub in enumerate(current_submission):
            if sub["student_id"] == cursub["student_id"] and sub["sheet_id"] == cursub["sheet_id"]:
                found_correct_student_and_sheet = True
                if sub["time"] > cursub["time"]:
                    found_older_submission_index = index
                break

        if not found_correct_student_and_sheet:
            # We found no previous submission from this student for this sheet
            current_submission.append(sub)
        elif found_older_submission_index > -1:
            # We found the student/sheet combination but it is older (based on the timestamp)
            # than the one we are checking for
            current_submission[found_older_submission_index] = sub

    return current_submission


def get_all_newest(db):
    db.cursor.execute("""SELECT id, sheet_id, student_id, time, files_path FROM
                         submission ORDER BY time DESC""")
    rows = db.cursor.fetchall()

    registered = set()
    submissions = []
    for row in rows:
        id, sheet_id, student_id, time, files_path = row
        if (sheet_id, student_id) in registered:
            continue
        registered.add((sheet_id, student_id))
        submissions.append(Submission(*row))

    return submissions


def get_from_id(db, submission_id):
    db.cursor.execute("""SELECT id, sheet_id, student_id, time, files_path, deleted FROM submission
                         WHERE id = ?""", (submission_id, ))
    row = db.cursor.fetchone()
    if not row:
        raise ValueError('Cannot find submission')
    return Submission(*row)
