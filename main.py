#!/usr/bin/env python

from __future__ import unicode_literals


import imaplib
import smtplib
import time
import json
import logging
import hashlib
import sys
from email.parser import Parser
import email
import sqlite3
import base64
import re
import os

# useful for debugging: $ openssl s_client -crlf -connect imap.gmail.com:993


class mailContainer(object):
    imapmail = 0
    mails = []

    def __init__(self,imap,uid,temp):
        self.imapmail = imap
        self.uidlist = uid
        self.templates = temp

class mailElement(object):
    uid = -1
    templates = []
    email = ""

    def __init__(self,uid,templates,email):
        self.uid = uid
        self.templates = templates
        self.email = email
        self.templates["MAILFROM"] = email["From"]
        self.templates["MAILDATE"] = email["Date"]
        self.templates["MAILRECEIVED"] = email["Received"]


#
# core functions
#

def main():
    # patching imaplib
    imaplib.Commands["MOVE"] = ("SELECTED",)
    imaplib.Commands["IDLE"] = ("AUTH","SELECTED",)
    imaplib.Commands["DONE"] = ("AUTH","SELECTED",)

    # Parsing config.json, making the settings global
    global settings,templates
    configFile = json.load(open("config.json"))
    settings = configFile["settings"]
    templates = configFile["templates"]

    loglevel = settings.get("loglevel","ERROR")
    if loglevel == "ALL":
        logging.basicConfig(format="%(asctime)s %(message)s",level=logging.DEBUG)
    elif loglevel == "ERROR":
        logging.basicConfig(format="%(asctime)s %(message)s",level=logging.ERROR)
    elif loglevel == "CRITICAL":
        logging.basicConfig(format="%(asctime)s %(message)s",level=logging.CRITICAL)

    rules = configFile["rules"]

    imapmail = login()
    imapmail._command("IDLE")
    

    if "idling" in imapmail.readline():
        logging.debug("Server supports IDLE.")
        firstRun = True
        while(True):
            if "EXISTS" in imapmail.readline() or firstRun:
                imapmail._command("DONE")
                imapmail.readline()
                for rule in rules:
                    processRule(mailContainer(imapmail,[],templates),rule["steps"])
                imapmail._command("IDLE")
            firstRun = False
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while(True):
            processRule(mailContainer(imapmail,[],templates),rules)
            for rule in rules:
                processRule(mailContainer(imapmail,[],templates),rule["steps"])
            time.sleep(settings.get("delay"))

def login():
    imapmail = imaplib.IMAP4_SSL(settings.get("imapmail_server"))
    imapmail.login(settings.get("mail_address"), settings.get("mail_password"))
    imapmail.select()
    logging.info("IMAP login (%s on %s)" % (settings.get("mail_address"),settings.get("imapmail_server")))

    return imapmail

def smtpMail(to,what):
    smtpmail = smtplib.SMTP(settings.get("smtpmail_server"))
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(settings.get("mail_address"), settings.get("mail_password"))
    smtpmail.sendmail(settings.get("mail_address"), to, what)
    smtpmail.quit()


def debug_print(msg):
    if settings.get('debug') == 1:
        print(msg)

def processRule(mailcontainer,rule):
    debug_print("**** rule")
    for step in rule:
        debug_print("* exec: %s" % step[0])
        mailcontainer = getattr(sys.modules[__name__],"rule_" + step[0])(mailcontainer,*step[1:])
        if not mailcontainer:
            break
        if not mailcontainer.mails:
            break
        debug_print("*  ret %d mails" % len(mailcontainer.mails))
    debug_print("**** done\n")


#
# rule functions
#

def rule_filter(mailcontainer,filterVariable,filterValue,mailbox="inbox"):
    # returns all mails where filterVariable == filterValue

    # see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
    # and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
    mailcontainer.imapmail.select(mailbox)

    data = imapCommand(mailcontainer.imapmail,"search","ALL","*")
    if data != ['']:
        if filterVariable == "ALL":
            return data
        
        for uid in data:
            if uid:
                data = Parser().parsestr(imapCommand(mailcontainer.imapmail,"fetch",uid,"(rfc822)")[0][1])
                if filterValue.upper() in data[filterVariable].upper():
                    mailcontainer.mails.append(mailElement(uid,templates,data))
    return mailcontainer

def rule_answer(mailcontainer,subject,text,address="(back)"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
    for mail in mailcontainer.mails:
        hashobj = hashlib.md5()
        hashobj.update(subject + text)
        subject_hash = hashobj.hexdigest()

        if address == "(back)":
            client_mail_addr = mail.email["From"]
        else:
            client_mail_addr = address

        if "NETSEC-Answered-" + subject_hash in imapCommand(mailcontainer.imapmail,"fetch",mail.uid,"FLAGS"):
            logging.error("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(mail.uid,client_mail_addr,subject))
        else:
            if "noreply" in client_mail_addr:
                logging.error("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(mail.uid,client_mail_addr,subject))
            else:
                smtpMail(client_mail_addr,"Content-Type:text/html\nSubject: %s\n\n%s"%(checkForTemplate(mail,subject),checkForTemplate(mail,text)))
                rule_flag(mailContainer(mailcontainer.imapmail,mail,[]),"NETSEC-Answered-" + subject_hash)
    return mailcontainer

def rule_move(mailcontainer,destination):
    # moves the mails from id_list to mailbox destination
    # warning: this alters the UID of the mails!
    mailcontainer.imapmail.create(destination)
    for mail in mailcontainer.mails:
        # https://tools.ietf.org/html/rfc6851
        imapCommand(mailcontainer.imapmail,"MOVE",mail.uid,destination)
    # no "return mailcontainer" here, because the UIDs are invalid after movement.

def rule_flag(mailcontainer,flag):
    for mail in mailcontainer.mails:
        imapCommand(mailcontainer.imapmail,"STORE",mail.uid,"+FLAGS",flag.replace("\\","\\\\")) # could interpret \NETSEC as <newline>ETSEC
    return mailcontainer

def rule_log(mailcontainer,lvl,msg):
    if lvl == "LOG":
        logging.debug(msg)
    else:
        logging.error(msg)
    return mailcontainer

def rule_delete(mailcontainer):
    rule_flag(mailcontainer,"DELETE")
    mailcontainer.imapmail.expunge()

def rule_save(mailcontainer):
    if settings.get("savemode") == "db":
        sqldatabase = sqlite3.connect(settings.get("database"))
        cursor = sqldatabase.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS inbox (addr text,date text,subject text,korrektor text,attachment blob)")

        for mail in mailcontainer.mails:
            mail = mail.email
            insertValues = [mail["From"],mail["Date"],mail["Subject"],"(-)"]
            attachments = []

            for payloadPart in mail.walk():
                if payloadPart.get("Content-Transfer-Encoding"):
                    if "base64" in payloadPart.get("Content-Transfer-Encoding"):
                        attachments.append(payloadPart.get_payload())
                    else:
                        attachments.append(base64.b64encode(payloadPart.get_payload()))
            insertValues.append("$".join(attachments))

            cursor.execute("INSERT INTO inbox VALUES (?,?,?,?,?)",insertValues)
            sqldatabase.commit()
            sqldatabase.close()
    elif settings.get("savemode") == "file":
        retdir = os.getcwd()

        for mail in mailcontainer.mails:
            mail = mail.email

            if not os.path.exists("attachments"):
                os.mkdir("attachments")
            os.chdir("attachments")

            if not os.path.exists(mail["From"]):
                os.mkdir(mail["From"])
            os.chdir(mail["From"])

            if not os.path.exists(mail["Date"]):
                os.mkdir(mail["Date"])
            os.chdir(mail["Date"])

            for payloadPart in mail.walk():
                if payloadPart.get_filename():
                    attachFile = open(payloadPart.get_filename(),"w")
                elif payloadPart.get_payload():
                    attachFile = open("mailtext.txt","a")
                else:
                    pass
                attachFile.write(str(payloadPart.get_payload(decode="True")))
                attachFile.close()
            os.chdir(retdir)
    return mailcontainer


#
# helper functions
#

def checkForTemplate(mail,raw):
    varInRaw = re.findall("\$([A-Z]*)",raw)
    if varInRaw:
        for var in varInRaw:
            if var in mail.templates:
                raw = raw.replace("$" + var,checkForTemplate(mail,mail.templates[var]))
    return raw

def imapCommand(imapmail,command,uid,*args):
    debug_print("\t%s %s %s" % (command, uid, " ".join(args)))

    # IMAP Command caller with error handling
    if uid:
        code, ids = imapmail.uid(command, uid, *args)
    else:
        code, ids = imapmail.uid(command, *args)

    if "OK" in code:
        return ids
    else:
        logging.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        raise self.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        return []

if __name__ == "__main__":
    main()
