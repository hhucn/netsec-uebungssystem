from __future__ import unicode_literals

import hashlib
import logging
import email
import os
import re
import time
import imp

from . import helper
from .mail import Mail


def filter(config, imapmail, mails, filterCriteria, mailbox="inbox"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
    # and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
    imapmail.select(mailbox)

    response = helper.imapCommand(imapmail, "UID", "SEARCH", filterCriteria)
    mails = []

    if response:
        response = response.encode("utf-8").split(" ")
        for uid in response:
            mailInfo, mailText = helper.imapCommand(imapmail, "UID", "FETCH", uid, "(rfc822)")
            data = email.message_from_string(mailText)
            mails.append(Mail(uid, config("variables"), data))
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
            flag(imapmail, [mail], "NETSEC-Answered-" + subjectHash)
    return mails


def move(config, imapmail, mails, destination):
    imapmail.create("\"%s\"" % destination)

    for mail in mails:
        # https://tools.ietf.org/html/rfc6851
        helper.imapCommand(imapmail, "UID", "MOVE", mail.uid, "\"%s\"" % destination)
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
    flag(imapmail, mails, "\\DELETED")
    imapmail.expunge()


def save(config, imapmail, mails):
    for mail in mails:
        clientMailAddress = re.search(r"([^\@\<]*)\@([^\@\>]*)", mail.variables["MAILFROM"])
        clientIdentifier = clientMailAddress.group(1)
        attachPath = os.path.join(config("attachment_path"), helper.escapePath(clientIdentifier))
        timestamp = str(int(time.time()))

        if not os.path.exists(attachPath):
            os.makedirs(attachPath)

        for payloadPart in mail.text.walk():
            if payloadPart.get_filename():
                attachFile = open(os.path.join(attachPath, timestamp + " " +
                                               helper.escapePath(payloadPart.get_filename())), "w")
            elif payloadPart.get_payload():
                attachFile = open(os.path.join(attachPath, "mailtext.txt"), "a")
            else:
                pass

            dataToWrite = str(payloadPart.get_payload(decode="True"))

            if dataToWrite:
                attachFile.write(dataToWrite)
            attachFile.close()
    return mails


def script(config, imapmail, mails, name, *args):
    try:
        loadedScript = imp.load_source(name, os.path.join(config("script_path"), "%s.py" % name))
    except ImportError:
        logging.error("Exception thrown while loading script '%s.py'." % name)
        return mails

    return loadedScript.run(imapmail, mails, *args)
