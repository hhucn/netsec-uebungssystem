from __future__ import unicode_literals

import collections
import re

from . import sheet, student

Submission = collections.namedtuple(
    'Submission',
    ['id', 'sheet_id', 'student_id', 'time'])


def sheet_by_mail(database, message):
    subject = message.get('Subject', '')
    sheet_m = re.match(r'Abgabe\s*(?P<id>[0-9]+)', subject)
    if not sheet_m:
        raise helper.MailError('Invalid subject line, found: %s', subject)
    sheet_id_str = sheet_m.group('id')
    assert re.match(r'^[0-9]+$', sheet_id_str)
    sheet_id = int(sheet_id_str)

    return sheet.get_by_id(database, sheet_id)


def handle_mail(config, database, message):
    alias = message.get('From', 'anonymous')
    s = student.resolve_alias(database, alias)
    sheet = sheet_by_mail(database, message)
    if not sheet:
        raise ValueError('Unsupported sheet')

    raise ValueError('would save now - disabled for now')

    mail_dt = dateutil.parser.parse(message["Date"])
    timestamp_str = mail_dt.isoformat()
    database = Database(config)
    submission_id = database.createSubmission(sheet_id, user_id)

    files_path = os.path.join(
        config("attachment_path"),
        helper.escape_filename(user_id),
        helper.escape_filename(sheet_id),
        helper.escape_filename(timestamp_str)
    )

    if os.path.exists(files_path):
        orig_files_path = files_path
        for i in itertools.count(2):
            files_path = '%s___%s' % (orig_files_path, i)
            if not os.path.exists(files_path):
                break

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

        submission_id
        database.addFileToSubmission(submission_id, "sha", payload_name, payload_path)

    commands.move(config, imapmail, mails, "Abgaben")