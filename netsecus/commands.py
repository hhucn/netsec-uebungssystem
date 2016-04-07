from __future__ import unicode_literals

import dateutil.parser
import email
import hashlib
import itertools
import logging
import os
import re

from . import helper
from .database import Database


def filter(config, imapmail, mails, filterCriteria, mailbox="inbox"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
    # and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
    imapmail.select(mailbox)

    response = helper.uidCommand(imapmail, "SEARCH", filterCriteria)
    mails = []

    response_ids = response.decode("utf-8").split(" ")
    for uid in response_ids:
        if uid:  # if inbox is empty, "uid" contains an empty string
            _mail_info, mail_bytes = helper.uidCommand(imapmail, "FETCH", uid, "(rfc822)")
            message = email.message_from_bytes(mail_bytes)
            mails.append((uid, message))
    return mails


def answer(config, imapmail, mails, subject, text, address="(back)"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
    for mail in mails:
        stringToHash = "%s: %s" % (subject, text)
        hashObject = hashlib.sha256()
        hashObject.update(stringToHash.encode("utf-8"))
        subjectHash = hashObject.hexdigest()

        if address == "(back)":
            clientMailAddress = mail.variables["MAILFROM"]
        else:
            clientMailAddress = address

        mail_flags = helper.imapCommand(imapmail, "UID", "FETCH", mail.uid, "FLAGS")
        if "NETSEC-Answered-" + subjectHash in mail_flags.encode("utf-8"):
            logging.error(
                "Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered." % (
                    mail.uid, clientMailAddress, subject))
        else:
            headers = ("Content-Type:text/html\nSubject: %s\n\n%s" % (
                helper.processVariable(mail.variables, subject),
                helper.processVariable(mail.variables, text)))
            helper.smtpMail(config, clientMailAddress, headers)
            flag(config, imapmail, [mail], "NETSEC-Answered-" + subjectHash)
    return mails


def move(config, imapmail, mails, destination):
    imapmail.create("\"%s\"" % destination)

    for mail in mails:
        # https://tools.ietf.org/html/rfc6851
        uid = mail[0]
        helper.imapCommand(imapmail, "UID", "MOVE", uid, "\"%s\"" % destination)
    return mails


def flag(config, imapmail, mails, flag):
    for mail in mails:
        helper.imapCommand(imapmail, "UID", "STORE", mail.uid, "+FLAGS", flag)
    return mails


def log(config, imapmail, mails, msg, lvl="ERROR"):
    if lvl == "DEBUG":
        logging.debug("Log: " + msg)
    else:
        logging.error("Log: " + msg)
    return mails


def delete(config, imapmail, mails):
    flag(config, imapmail, mails, "\\DELETED")
    imapmail.expunge()


# TODO do name resolution etc. here
def user_identifier(config, message):
    user_id = message.get('From', 'anonymous')
    database = Database(config)
    alias = database.resolveAlias(user_id)
    return alias


def sheet_identifier(message):
    subject = message.get('Subject', '')
    sheet_m = re.match(r'Abgabe\s*(?P<id>[0-9]+)', subject)
    if not sheet_m:
        raise helper.MailError('Invalid subject line, found: %s', subject)
    sheet_id = sheet_m.group('id')
    assert re.match(r'^[0-9]+$', sheet_id)
    return sheet_id


def save(config, imapmail, message):
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
