from __future__ import unicode_literals

import logging
import email
import sqlite3
import base64
import os
import re
import time

import helper


class mailElement(object):

    def __init__(self, uid, var, text):
        self.uid = uid
        self.variables = var
        self.text = text
        self.variables["MAILFROM"] = re.findall(r"\<(.*)\>", text["From"])[0]
        self.variables["MAILDATE"] = text["Date"]
        self.variables["MAILRECEIVED"] = text["Received"]


def filter(imapmail, mails, filterCriteria, mailbox="inbox"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
    # and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
    imapmail.select(mailbox)

    data = helper.imapCommand(imapmail, "search", filterCriteria)[0]

    mails = []

    for uid in data.split():
        a = helper.imapCommand(imapmail, "fetch", uid, "(rfc822)")[0][1].decode("utf-8")
        a = a.encode("ascii", "ignore")
        data = email.message_from_string(a)
        mails.append(mailElement(uid, helper.getConfigValue("variables"), data))
    return mails


def answer(imapmail, mails, subject, text, address="(back)"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
    if isinstance(mails, mailElement):
        mails = [mails]

    for mail in mails:
        subjectHash = helper.md5sum("%s: %s" % (subject, text))

        if address == "(back)":
            clientMailAddress = mail.variables["MAILFROM"]
        else:
            clientMailAddress = address

        mail_flags = helper.imapCommand(imapmail, "fetch", mail.uid, "FLAGS")[0]
        if "NETSEC-Answered-" + subjectHash in mail_flags.decode("utf-8"):
            logging.error(
                "Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered." % (
                    mail.uid, clientMailAddress, subject))
        else:
            helper.smtpMail(clientMailAddress, "Content-Type:text/html\nSubject: %s\n\n%s" %
                            (helper.checkForVariable(mail, subject), helper.checkForVariable(mail, text)))
            flag(imapmail, mail, "NETSEC-Answered-" + subjectHash)
    return mails


def move(imapmail, mails, destination):
    # moves the mails from id_list to mailbox destination
    # warning: this alters the UID of the mails!
    if isinstance(mails, mailElement):
        mails = [mails]

    imapmail.create(destination)
    for mail in mails:
        # https://tools.ietf.org/html/rfc6851
        helper.imapCommand(imapmail, "MOVE", mail.uid, destination)
    return mails


def flag(imapmail, mails, flag):
    if isinstance(mails, mailElement):
        mails = [mails]

    for mail in mails:
        helper.imapCommand(imapmail, "STORE", mail.uid, "+FLAGS", flag)
    return mails


def log(imapmail, mails, msg, lvl="ERROR"):
    if lvl == "DEBUG":
        logging.debug(msg)
    else:
        logging.error(msg)
    return mails


def delete(imapmail, mails):
    flag(imapmail, mails, "\\DELETED")
    imapmail.expunge()


def save(imapmail, mails):
    if isinstance(mails, mailElement):
        mails = [mails]

    if helper.getConfigValue("settings")["savemode"] == "db":
        sqldatabase = sqlite3.connect(helper.getConfigValue("settings")["database"])
        cursor = sqldatabase.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS inbox (addr text,date text,subject text,korrektor text,attachment blob)")

        for mail in mails:
            insertValues = [mail["From"], mail["Date"], mail["Subject"], "(-)"]
            attachments = []

            for payloadPart in mail.walk():
                if payloadPart.get("Content-Transfer-Encoding"):
                    if "base64" in payloadPart.get("Content-Transfer-Encoding"):
                        attachments.append(payloadPart.get_payload())
                    else:
                        attachments.append(base64.b64encode(payloadPart.get_payload()))
            insertValues.append("$".join(attachments))

            cursor.execute("INSERT INTO inbox VALUES (?,?,?,?,?)", insertValues)
            sqldatabase.commit()
            sqldatabase.close()
    elif helper.getConfigValue("settings")["savemode"] == "file":
        for mail in mails:
            clientMailAddress = re.findall(r"(.*)\@.*", mail.variables["MAILFROM"])[0].lower()

            if not os.path.exists("attachments"):
                os.mkdir("attachments")

            if not os.path.exists(clientMailAddress):
                os.mkdir(clientMailAddress)

            for payloadPart in mail.text.walk():
                if payloadPart.get_filename():
                    attachFile = open("attachments/%s/" % clientMailAddress + str(int(time.time())) + " " +
                                      payloadPart.get_filename(), "w")
                elif payloadPart.get_payload():
                    attachFile = open("attachments/%s/" % clientMailAddress + "mailtext.txt", "a")
                else:
                    pass

                dataToWrite = str(payloadPart.get_payload(decode="True"))

                if dataToWrite:
                    attachFile.write(dataToWrite)
                attachFile.close()
    return mails
