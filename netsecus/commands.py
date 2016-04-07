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
        # helper.imapCommand(imapmail, "UID", "MOVE", uid, "\"%s\"" % destination)
        helper.imapCommand(imapmail, "UID", "COPY", uid, "\"%s\"" % destination)
        helper.imapCommand(imapmail, "UID", "STORE", uid, "+FLAGS", "(\DELETED)")
        helper.imapCommand(imapmail, "UID", "EXPUNGE", uid)
    return mails


def flag(config, imapmail, mails, flag):
    for mail in mails:
        helper.imapCommand(imapmail, "UID", "STORE", mail, "+FLAGS", flag)
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
