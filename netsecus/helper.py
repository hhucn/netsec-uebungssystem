from __future__ import unicode_literals

import logging
import json
import re
import smtplib
import hashlib
import os


def setupLogging():
    if getConfigValue("settings", "loglevel") == "ERROR":
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.ERROR)
    else:
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def checkForVariable(mail, raw):
    varInRaw = re.findall(r"\$([A-Z]*)", raw)
    if varInRaw:
        for var in varInRaw:
            if var in mail.variables:
                raw = raw.replace("$" + var, checkForVariable(mail, mail.variables[var]))
    return raw


def imapCommand(imapmail, command, uid, *args):
    logging.debug("\t%s %s %s" % (command, uid, " ".join(args)))

    # IMAP Command caller with error handling
    if uid:
        code, ids = imapmail.uid(command, uid, *args)
    else:
        code, ids = imapmail.uid(command, *args)

    if "OK" in code:
        return [singleID.decode("utf-8") if isinstance(singleID, str) else singleID for singleID in ids]
    else:
        logging.error("Server responded with Code '%s' for '%s %s %s'." % (code, command, uid, args))
        raise OSError.ConnectionError("Server responded with Code '%s' for '%s %s %s'." % (code, command, uid, args))
        return []


def getConfigValue(*args):
    defaultsValue = json.load(open("config_default.json"))

    if os.path.isfile("config.json"):
        userValue = json.load(open("config.json"))
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

    logging.error("Tried to access config value at path %s, which doesn't exist." % "/".join(args))


def smtpMail(to, what):
    smtpmail = smtplib.SMTP(getConfigValue("login", "smtpmail_server"))
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(getConfigValue("login", "mail_address"), getConfigValue("login", "mail_password"))
    smtpmail.sendmail(getConfigValue("login", "mail_address"), to, what)
    smtpmail.quit()


def md5sum(what):
    hashobj = hashlib.md5()
    hashobj.update(what.encode("utf-8"))
    return hashobj.hexdigest()
