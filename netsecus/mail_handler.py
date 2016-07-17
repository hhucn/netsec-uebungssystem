from __future__ import unicode_literals

import logging
import time
import traceback

from . import database
from . import helper
from . import commands
from . import submission
from . import mail_helper


def mail_main(config):
    try:
        mail_run(config)
    except BaseException as e:
        on_error(config, e)
        raise


def mail_run(config):
    db = database.Database(config)
    helper.patch_imaplib()
    ignored_uids = set()
    while True:
        try:
            mainloop(config, db, ignored_uids)
        except (OSError, helper.MailConnectionError) as e:
            on_error(config, e)
        time.sleep(config("mail.delay"))


def on_error(config, e):
    logging.exception(e)
    if config('loglevel') == 'debug':
        traceback.print_exc()


def mainloop(config, db, ignored_uids):
    try:
        username = config('mail.username')
    except KeyError:
        username = config('mail.address')

    imapmail = mail_helper.loginIMAP(
        config("mail.imap_server"),
        username,
        config("mail.password"),
        config("mail.ssl"),
        config("loglevel") == "debug")

    imapmail._command("CAPABILITY")
    capabilities = imapmail.readline().decode("utf-8")
    helper.checkResult(imapmail, b"OK")
    if "UTF8" in capabilities:
        imapmail._command("ENABLE", "UTF8")
        helper.checkResult(imapmail, b"ENABLED")
        helper.checkResult(imapmail, b"OK")
        imapmail._command("ENABLE", "UTF8=ACCEPT")
        helper.checkResult(imapmail, b"ENABLED")
        helper.checkResult(imapmail, b"OK")
        logging.debug("Server supports UTF8")

    imapmail._command("IDLE")  # Check whether server supports IDLE
    if "idling" in imapmail.readline().decode("utf-8"):
        def idle_loop():
            imapmail.send(b"DONE\r\n")
            imapmail.readline()
            mailProcessing(config, db, imapmail, ignored_uids)
            imapmail._command("IDLE")
            logging.debug("Entering IDLE state.")

        logging.debug("Server supports IDLE.")
        idle_loop()
        while True:
            line = imapmail.readline().decode("utf-8")
            if not line:
                raise helper.MailConnectionError('Connection interrupted')
            if "EXISTS" in line:
                # We got mail!
                idle_loop()
    else:
        logging.debug("Server lacks support for IDLE... Falling back to delay.")
        while True:
            try:
                mailProcessing(config, db, imapmail, ignored_uids)
                time.sleep(config("mail.delay"))
            except KeyboardInterrupt:
                mail_helper.logoutIMAP(imapmail)
                raise


def mailProcessing(config, db, imapmail, ignored_uids):
    filterCriteria = "SUBJECT \"Abgabe\" UNDELETED"
    mails = commands.filter(config, imapmail, [], filterCriteria)
    for uid, message in mails:
        if uid in ignored_uids:
            continue
        try:
            submission.handle_mail(config, db, imapmail, uid, message)
        except helper.MailError as me:
            ignored_uids.add(me.uid)
            on_error(config, me)
