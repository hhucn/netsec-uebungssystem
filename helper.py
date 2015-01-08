import logging

def checkForTemplate(mail,raw):
    varInRaw = re.findall("\$([A-Z]*)",raw)
    if varInRaw:
        for var in varInRaw:
            if var in mail.variables:
                raw = raw.replace("$" + var,checkForTemplate(mail,mail.variables[var]))
    return raw

def imapCommand(imapmail,command,uid,*args):
    logging.debug("\t%s %s %s" % (command, uid, " ".join(args)))

    # IMAP Command caller with error handling
    if uid:
        code, ids = imapmail.uid(command, uid, *args)
    else:
        code, ids = imapmail.uid(command, *args)

    if "OK" in code:
        return ids
    else:
        logging.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        raise self.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
        return []