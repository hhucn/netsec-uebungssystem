#!/usr/bin/env python

from __future__ import unicode_literals


import imaplib
import time
import logging
import sys

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

    logging.basicConfig(format="%(asctime)s %(message)s",level=(logging.ERROR if helper.getConfigValue("settings")["loglevel"] == "ERROR" else logging.DEBUG))

    imapmail = loginIMAP(helper.getConfigValue("login")["imapmail_server"],helper.getConfigValue("login")["mail_address"],helper.getConfigValue("login")["mail_password"])
    imapmail._command("IDLE")
    

    if "idling" in imapmail.readline():
        logging.debug("Server supports IDLE.")
        firstRun = True
        while(True):
            if firstRun or "EXISTS" in imapmail.readline():
                imapmail._command("DONE")
                imapmail.readline()
                ruleLoop(imapmail)
                imapmail._command("IDLE")
            firstRun = False
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while(True):
            ruleLoop(imapmail)
            time.sleep(helper.getConfigValue("settings")["delay"])

def ruleLoop(imapmail):
    for rule in helper.getConfigValue("rules"):
        processRule(imapmail,rule["steps"])

def processRule(imapmail,rule):
    logging.debug("**** rule")

    mails = []

    for step in rule:
        logging.debug("* exec: %s" % step[0])
        mails = getattr(sys.modules["rules"],step[0])(imapmail,mails,*step[1:])
        if not mails:
            break
        logging.debug("*  ret %d mail(s)" % len(mails))
    logging.debug("**** done\n")

def loginIMAP(server,address,password):
    imapmail = imaplib.IMAP4_SSL(server)
    imapmail.login(address,password)
    imapmail.select()
    logging.info("IMAP login (%s on %s)"%(address,server))
    return imapmail

if __name__ == "__main__":
    main()