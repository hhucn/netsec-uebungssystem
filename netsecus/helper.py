from __future__ import unicode_literals

import imaplib
import logging
import os
import re
import smtplib


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


def smtpMail(config, to, what):
    smtpmail = smtplib.SMTP(config("mail.smtp_server"))
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(config("mail.address"), config("mail.password"))
    smtpmail.sendmail(config("mail.address"), to, what)
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
