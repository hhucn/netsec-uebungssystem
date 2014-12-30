#!/usr/bin/env python

from __future__ import unicode_literals


import imaplib
import smtplib
import time
import json
import logging
import hashlib
import sys
import sqlite3
import base64
import re
import os

import helper
import rules

# useful for debugging: $ openssl s_client -crlf -connect imap.gmail.com:993
class mailContainer(object):
    imapmail = 0
    mails = []

    def __init__(self,imap,uid,temp):
        self.imapmail = imap
        self.uidlist = uid
        self.templates = temp
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
    rules = configFile["rules"]

    logging.basicConfig(format="%(asctime)s %(message)s",level=(logging.ERROR if settings.get("loglevel","ERROR") == "ERROR" else logging.DEBUG))

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

def processRule(mailcontainer,rule):
    logging.debug("**** rule")
    for step in rule:
        logging.debug("* exec: %s" % step[0])
        mailcontainer = getattr(sys.modules["rules"],step[0])(mailcontainer,*step[1:])
        if not mailcontainer:
            break
        if not mailcontainer.mails:
            break
        logging.debug("*  ret %d mail(s)" % len(mailcontainer.mails))
    logging.debug("**** done\n")

if __name__ == "__main__":
    main()