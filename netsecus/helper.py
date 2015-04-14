from __future__ import unicode_literals

import imaplib
import logging
import json
import re
import smtplib
import os

configPath = ""


def setupLogging():
    if getConfigValue("settings", "loglevel") == "ERROR":
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.ERROR)
    else:
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def processVariable(variables, text):
    return re.sub(r'\$([a-zA-Z0-9_]+)',
                  lambda m: processVariable(variables, str(variables[m.group(0)])),
                  text)


def imapCommand(imapmail, command, *args):
    logging.debug("\t%s %s" % (command, " ".join(args)))

    typ, dat = imapmail._simple_command(command, *args)

    if command == "UID":
        command = args[0]

    code, response = imapmail._untagged_response(typ, dat, command)
    response = response[0]  # the response ships within a list with one element; we need to unpack that.

    if "OK" in code:
        if response:
            return response
        return
    else:
        logging.error("Server responded with Code '%s' for '%s %s'." % (code, command, args))
        raise Exception("Server responded with Code '%s' for '%s %s'." % (code, command, args))
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

        logging.error("Tried to access config value at path '%s', which doesn't exist." % os.sep.join(args))


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
    imaplib.Commands["ENABLE"] = ("AUTH",)
    imaplib.Commands["CABABILITY"] = ("AUTH",)
    imaplib.IMAP4_SSL.send = imaplibSendPatch


def imaplibSendPatch(self, data):
    data = data.encode("utf-8")

    bytes = len(data)
    while bytes > 0:
        sent = self.sslobj.write(data)
        if sent == bytes:
            break    # avoid copy
        data = data[sent:]
        bytes = bytes - sent


def escapePath(path):
    if os.sep in path:
        logging.error("Found '%s' in '%s', possible attack." % (os.sep, path))
        path.replace(os.sep, "_")

    for pathElement in path.split(os.sep):
        if pathElement[0] == ".":
            logging.error("Found dot at beginning of filename, possible attack.")
            pathElement[0] = "_"

    return path
