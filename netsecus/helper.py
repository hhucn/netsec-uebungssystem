from __future__ import unicode_literals

import imaplib
import logging
import json
import re
import smtplib
import os


def setupLogging():
    if getConfigValue("settings", "loglevel") == "ERROR":
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.ERROR)
    else:
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def processVariable(mail, text):
    foundVarInText = re.findall(r"\$([^ .,\$\n\t])+", text)

    for var in foundVarInText:
        if var in mail.variables:
            text = text.replace("$" + var, processVariable(mail, mail.variables[var]))
    return text


def imapCommand(imapmail, command, uid, *args):
    logging.debug("\t%s %s %s" % (command, uid, " ".join(args)))

    # IMAP Command caller with error handling
    if uid:
        code, response = imapmail.uid(command, uid, *args)
    else:
        code, response = imapmail.uid(command, *args)

    if "OK" in code:
        response = response[0]
        if response:
            return response
        return
    else:
        logging.error("Server responded with Code '%s' for '%s %s %s'." % (code, command, uid, args))
        raise OSError.ConnectionError("Server responded with Code '%s' for '%s %s %s'." % (code, command, uid, args))
        return


def getConfigValue(*args):
    with open("config_default.json") as defaultsFile:
        defaultsValue = json.load(defaultsFile)
        if os.path.isfile(configPath):
            with open(configPath) as userFile:
                userValue = json.load(userFile)
                try:
                    for path in args:
                        userValue = userValue[path]
                    return userValue
                except KeyError:
                    pass
        try:
            for path in args:
                defaultsValue = defaultsValue[path]
            return defaultsValue
        except KeyError:
            pass

        logging.error("Tried to access config value at path %s, which doesn't exist." % os.sep.join(args))


def smtpMail(to, what):
    smtpmail = smtplib.SMTP(getConfigValue("login", "smtpmail_server"))
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(getConfigValue("login", "mail_address"), getConfigValue("login", "mail_password"))
    smtpmail.sendmail(getConfigValue("login", "mail_address"), to, what)
    smtpmail.quit()


def patch_imaplib():
    # imaplib is missing some essential commands.
    # Since we just need these passed through to the server, patch them in
    imaplib.Commands["MOVE"] = ("SELECTED",)
    imaplib.Commands["IDLE"] = ("AUTH", "SELECTED",)
    imaplib.Commands["DONE"] = ("AUTH", "SELECTED",)


def escapePath(path):
    if os.sep in path:
        logging.error("Found '%s' in '%s', possible attack." % (os.sep, path))
        path.replace(os.sep, "_")

    for pathElement in path.split(os.sep):
        if pathElement[0] == ".":
            logging.error("Found dot at beginning of filename, possible attack.")
            pathElement[0] = "_"
