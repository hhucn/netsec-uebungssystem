from __future__ import unicode_literals

import email
import logging

from . import helper


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


def move(config, imapmail, uid, destination):
    imapmail.create("\"%s\"" % destination)

    # https://tools.ietf.org/html/rfc6851
    # UID MOVE is not supported everywhere (works on gmail, but not hhu)
    # helper.imapCommand(imapmail, "UID", "MOVE", uid, "\"%s\"" % destination)

    helper.imapCommand(imapmail, "UID", "COPY", uid, "\"%s\"" % destination)
    helper.imapCommand(imapmail, "UID", "STORE", uid, "+FLAGS", "(\DELETED)")
    helper.imapCommand(imapmail, "UID", "EXPUNGE", uid)


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
