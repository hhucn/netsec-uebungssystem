import logging
import email
import sqlite3
import base64
import hashlib

import helper

class mailElement(object):
    def __init__(self,uid,var,email):
        self.uid = uid
        self.variables = var
        self.email = email
        self.variables["MAILFROM"] = email["From"]
        self.variables["MAILDATE"] = email["Date"]
        self.variables["MAILRECEIVED"] = email["Received"]

def filter(mailcontainer,filterVariable,filterValue,mailbox="inbox"):
    # returns all mails where filterVariable == filterValue

    # see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
    # and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
    mailcontainer.imapmail.select(mailbox)

    data = helper.imapCommand(mailcontainer.imapmail,"search","ALL","*")
    if data != ['']:
        if filterVariable == "ALL":
            return data
        
        for uid in data:
            if uid:
                data = email.message_from_string(helper.imapCommand(mailcontainer.imapmail,"fetch",uid,"(rfc822)")[0][1])
                if filterValue.upper() in data[filterVariable].upper():
                    mailcontainer.mails.append(mailElement(uid,variables,data))
    return mailcontainer

def answer(mailcontainer,subject,text,address="(back)"):
    # see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
    for mail in mailcontainer.mails:
        hashobj = hashlib.md5()
        hashobj.update(subject + text)
        subject_hash = hashobj.hexdigest()

        if address == "(back)":
            client_mail_addr = mail.email["From"]
        else:
            client_mail_addr = address

        if "NETSEC-Answered-" + subject_hash in helper.imapCommand(mailcontainer.imapmail,"fetch",mail.uid,"FLAGS")[0]:
            logging.error("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(mail.uid,client_mail_addr,subject))
        else:
            if "noreply" in client_mail_addr:
                logging.error("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(mail.uid,client_mail_addr,subject))
            else:
                smtpMail(client_mail_addr,"Content-Type:text/html\nSubject: %s\n\n%s"%(checkForVariable(mail,subject),checkForVariable(mail,text)))
                flag(mailContainer(mailcontainer.imapmail,mail,[]),"NETSEC-Answered-" + subject_hash)
    return mailcontainer

def move(mailcontainer,destination):
    # moves the mails from id_list to mailbox destination
    # warning: this alters the UID of the mails!
    mailcontainer.imapmail.create(destination)
    for mail in mailcontainer.mails:
        # https://tools.ietf.org/html/rfc6851
        helper.imapCommand(mailcontainer.imapmail,"MOVE",mail.uid,destination)
    # no "return mailcontainer" here, because the UIDs are invalid after movement.

def flag(mailcontainer,flag):
    for mail in mailcontainer.mails:
        helper.imapCommand(mailcontainer.imapmail,"STORE",mail.uid,"+FLAGS",flag.replace("\\","\\\\")) # could interpret \NETSEC as <newline>ETSEC
    return mailcontainer

def log(mailcontainer,lvl,msg):
    if lvl == "LOG":
        logging.debug(msg)
    else:
        logging.error(msg)
    return mailcontainer

def delete(mailcontainer):
    flag(mailcontainer,"DELETE")
    mailcontainer.imapmail.expunge()

def save(mailcontainer):
    if settings.get("savemode") == "db":
        sqldatabase = sqlite3.connect(settings.get("database"))
        cursor = sqldatabase.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS inbox (addr text,date text,subject text,korrektor text,attachment blob)")

        for mail in mailcontainer.mails:
            mail = mail.email
            insertValues = [mail["From"],mail["Date"],mail["Subject"],"(-)"]
            attachments = []

            for payloadPart in mail.walk():
                if payloadPart.get("Content-Transfer-Encoding"):
                    if "base64" in payloadPart.get("Content-Transfer-Encoding"):
                        attachments.append(payloadPart.get_payload())
                    else:
                        attachments.append(base64.b64encode(payloadPart.get_payload()))
            insertValues.append("$".join(attachments))

            cursor.execute("INSERT INTO inbox VALUES (?,?,?,?,?)",insertValues)
            sqldatabase.commit()
            sqldatabase.close()
    elif settings.get("savemode") == "file":
        retdir = os.getcwd()

        for mail in mailcontainer.mails:
            mail = mail.email

            if not os.path.exists("attachments"):
                os.mkdir("attachments")
            os.chdir("attachments")

            if not os.path.exists(mail["From"]):
                os.mkdir(mail["From"])
            os.chdir(mail["From"])

            if not os.path.exists(mail["Date"]):
                os.mkdir(mail["Date"])
            os.chdir(mail["Date"])

            for payloadPart in mail.walk():
                if payloadPart.get_filename():
                    attachFile = open(payloadPart.get_filename(),"w")
                elif payloadPart.get_payload():
                    attachFile = open("mailtext.txt","a")
                else:
                    pass
                attachFile.write(str(payloadPart.get_payload(decode="True")))
                attachFile.close()
            os.chdir(retdir)
    return mailcontainer
