#!/usr/bin/env python

from __future__ import unicode_literals


import imaplib
import smtplib
import time
import json
import logging
import sys
import os

import helper
import rules

# useful for debugging: $ openssl s_client -crlf -connect imap.gmail.com:993

#
# core functions
#

def main():
    # patching imaplib
    imaplib.Commands["MOVE"] = ("SELECTED",)
    imaplib.Commands["IDLE"] = ("AUTH","SELECTED",)
    imaplib.Commands["DONE"] = ("AUTH","SELECTED",)

    # Parsing config.json, making the settings global
    global settings,login
    configFile = json.load(open("config.json"))
    settings = configFile["settings"]
    variables = configFile["variables"]
    rules = configFile["rules"]
    login = json.load(open("login.json"))

    logging.basicConfig(format="%(asctime)s %(message)s",level=(logging.ERROR if settings.get("loglevel","ERROR") is "ERROR" else logging.DEBUG))

    imapmail = loginIMAP(login.get("imapmail_server"),login.get("mail_address"),login.get("mail_password"))
    imapmail._command("IDLE")
    

    if "idling" in imapmail.readline():
        logging.debug("Server supports IDLE.")
        firstRun = True
        while(True or firstRun):
            if "EXISTS" in imapmail.readline() or firstRun:
                imapmail._command("DONE")
                imapmail.readline()
                for rule in rules:
                    processRule(mailContainer(imapmail,[],variables),rule["steps"])
                imapmail._command("IDLE")
            firstRun = False
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while(True or firstRun):
            processRule(mailContainer(imapmail,[],variables),rules)
            for rule in rules:
                processRule(mailContainer(imapmail,[],variables),rule["steps"])
            time.sleep(settings.get("delay"))
            firstRun = False

def loginIMAP(server,address,password):
    imapmail = imaplib.IMAP4_SSL(server)
    imapmail.login(address,password)
    imapmail.select()
    logging.info("IMAP login (%s on %s)"%(address,server))
    return imapmail

def smtpMail(to,what):
    smtpmail = smtplib.SMTP(settings.get("smtpmail_server"))
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(login.get("mail_address"), login.get("mail_password"))
    smtpmail.sendmail(login.get("mail_address"), to, what)
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