import logging
import json
import re
import smtplib
import hashlib

def checkForVariable(mail,raw):
    varInRaw = re.findall("\$([A-Z]*)",raw)
    if varInRaw:
        for var in varInRaw:
            if var in mail.variables:
                raw = raw.replace("$" + var,checkForVariable(mail,mail.variables[var]))
    return raw

def imapCommand(imapmail,command,uid,*args):
    logging.debug("\t%s %s %s" % (command, uid, " ".join(args)))

    # IMAP Command caller with error handling
    if uid:
        code, ids = imapmail.uid(command, uid, *args)
    else:
        code, ids = imapmail.uid(command, *args)

    if "OK" in code:
        return [singleID.decode("utf-8") if isinstance(singleID,str) else singleID for singleID in ids]
    else:
        logging.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        raise self.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        return []

def getConfigValue(what):
    if "login" in what:
        return json.load(open("login.json"))
    return json.load(open("config.json"))[what]

def smtpMail(to,what):
    smtpmail = smtplib.SMTP(getConfigValue("login")["smtpmail_server"])
    smtpmail.ehlo()
    smtpmail.starttls()
    smtpmail.login(getConfigValue("login")["mail_address"],getConfigValue("login")["mail_password"])
    smtpmail.sendmail(getConfigValue("login")["mail_address"], to, what)
    smtpmail.quit()

def md5sum(what):
    hashobj = hashlib.md5()
    hashobj.update(what.encode("utf-8"))
    return hashobj.hexdigest()