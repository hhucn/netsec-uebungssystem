from __future__ import unicode_literals

import imaplib
import logging
import time

from . import helper
from . import rules


def mail_main(config):
    helper.patch_imaplib()
    while True:
        try:
            mainloop(config)
        except (OSError, helper.MailError) as e:
            logging.error(e)
        time.sleep(config("mail.delay"))


def mainloop(config):
    try:
        username = config('mail.username')
    except KeyError:
        username = config('mail.address')

    imapmail = loginIMAP(
        config("mail.imap_server"),
        username,
        config("mail.password"),
        config("mail.ssl"))

    imapmail._command("CAPABILITY")
    capabilities = imapmail.readline().decode("utf-8")
    helper.checkResult(imapmail, "OK")
    if "UTF8" in capabilities:
        imapmail._command("ENABLE", "UTF8")
        helper.checkResult(imapmail, "* ENABLED")
        helper.checkResult(imapmail, "OK")
        imapmail._command("ENABLE", "UTF8=ACCEPT")
        helper.checkResult(imapmail, "* ENABLED")
        helper.checkResult(imapmail, "OK")
        logging.debug("Server supports UTF8")

    imapmail._command("IDLE")

    if "idling" in imapmail.readline().decode("utf-8"):
        def idle_loop():
            imapmail._command("DONE")
            imapmail.readline()
            mailProcessing(config, imapmail)
            imapmail._command("IDLE")
            logging.debug("Entering IDLE state.")

        logging.debug("Server supports IDLE.")
        idle_loop()
        while True:
            line = imapmail.readline().decode("utf-8")
            if not line:
                raise helper.MailError('Connection interrupted')
            if "EXISTS" in line:
                # We got mail!
                idle_loop()
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while True:
            try:
                mailProcessing(config, imapmail)
                time.sleep(config("mail.delay"))
            except KeyboardInterrupt:
                logoutIMAP(imapmail)
                raise


def mailProcessing(config, imapmail):
    filterCriteria = """SUBJECT "Abgabe" """
    uids = rules.filter(config, imapmail, [], filterCriteria)
    uids = rules.save(config, imapmail, uids)
    uids = rules.move(config, imapmail, "Abgaben")


def ruleLoop(config, imapmail):
    for rule in config("rules"):
        processRule(config, imapmail, rule)


def processRule(config, imapmail, rule):
    logging.debug("**** rule: '%s'" % rule["title"])

    mails = []

    for step in rule["steps"]:
        logging.debug("* exec: %s" % step[0])
        mails = getattr(rules, step[0])(config, imapmail, mails, *step[1:])

        if not mails:
            logging.debug("*  ret no mails")
            break
        logging.debug("*  ret %d mail(s)" % len(mails))
    logging.debug("**** done: '%s'" % rule["title"])


def loginIMAP(server, address, password, ssl=True):
    if not address or not password:
        err = "IMAP login information incomplete. (Missing address or password)"
        logging.error(err)
        raise ValueError(err)
    else:
        if ssl:
            imapmail = imaplib.IMAP4_SSL(server)
        else:
            imapmail = imaplib.IMAP4(server)
        imapmail.login(address, password)
        logging.debug("IMAP login (%s on %s)" % (address, server))
    return imapmail


def logoutIMAP(imapmail):
    imapmail.close()
    imapmail.logout()
    logging.debug("IMAP logout")
