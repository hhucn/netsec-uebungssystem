from __future__ import unicode_literals

import argparse
import imaplib
import logging
import time

from . import helper
from . import rules


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "-config", default="config.json",
                        help="Path to the config.json to be used", dest="configPath")
    args = vars(parser.parse_args())
    helper.configPath = args["configPath"]

    helper.patch_imaplib()
    helper.setupLogging()

    imapmail = loginIMAP(
        helper.getConfigValue("login", "imapmail_server"),
        helper.getConfigValue("login", "mail_address"),
        helper.getConfigValue("login", "mail_password"))
    imapmail._command("IDLE")

    if "idling" in imapmail.readline().decode("utf-8"):
        logging.debug("Server supports IDLE.")
        firstRun = True
        while True:
            if firstRun or "EXISTS" in imapmail.readline().decode("utf-8"):
                imapmail._command("DONE")
                imapmail.readline()
                ruleLoop(imapmail)
                imapmail._command("IDLE")
                logging.debug("Entering IDLE state.")
            firstRun = False
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while True:
            ruleLoop(imapmail)
            time.sleep(helper.getConfigValue("settings", "delay"))


def ruleLoop(imapmail):
    for rule in helper.getConfigValue("rules"):
        processRule(imapmail, rule)


def processRule(imapmail, rule):
    logging.debug("**** rule: '%s'" % rule["title"])

    mails = []

    for step in rule["steps"]:
        logging.debug("* exec: %s" % step[0])
        mails = getattr(rules, step[0])(imapmail, mails, *step[1:])

        if not mails:
            logging.debug("*  ret no mails")
            break
        logging.debug("*  ret %d mail(s)" % len(mails))
    logging.debug("**** done: '%s'" % rule["title"])


def loginIMAP(server, address, password):
    imapmail = imaplib.IMAP4_SSL(server)
    imapmail.login(address, password)
    imapmail.select()
    logging.info("IMAP login (%s on %s)" % (address, server))
    return imapmail
