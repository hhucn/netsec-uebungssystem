from __future__ import unicode_literals

import collections

Submission = collections.namedtuple(
    'Submission',
    ['id', 'sheet_id', 'student_id', 'time'])


def save_from_mail(config, message):
    user_id = user_identifier(config, message)
    sheet_id = sheet_identifier(message)
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
