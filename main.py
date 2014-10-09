from __future__ import unicode_literals

import __imaplib as imaplib
import smtplib
from time import sleep
import datetime
import ConfigParser


def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)
	
	# Parsing config.ini, making the settings global
	global smtpmail_server,imapmail_server,mail_address,mail_password,log_level,delay
	configFile = ConfigParser.ConfigParser()
	configFile.read("config.ini")
	smtpmail_server = configFile.get("Basic","smtpmail_server").replace("\"","")
	imapmail_server = configFile.get("Basic","imapmail_server").replace("\"","")
	mail_address    = configFile.get("Basic","mail_address").replace("\"","")
	mail_password   = configFile.get("Basic","mail_password").replace("\"","")
	log_level = int(configFile.get("Basic","log_level"))
	delay     = float(configFile.get("Basic","delay"))

	imapmail = login()
	while(True):
		# nesting, like in jQuery, are possible because the functions return an id_list.
		# moveMails(imapmail,answerMails(imapmail,filterInbox(imapmail,"Subject","Aufgabe","Inbox"),"Mail eingegangen","Ihre E-Mail ist eingegangen"),"Unbearbeitet")
		# for debugging reasons (and because it's not really beautiful code), it should be used like this:
		id_list = filterInbox(imapmail,"Subject","Aufgabe")
		answerMails(imapmail,id_list,"Mail eingegangen!","Ihre Mail ist eingegangen.")
		moveMails(imapmail,id_list,"Unbearbeitet")
		sleep(delay)

def login():
	imapmail = imaplib.IMAP4_SSL(imapmail_server)
	imapmail.login(mail_address, mail_password)
	imapmail.select()
	log("IMAP login (%s on %s)" % (mail_address,imapmail_server),2)

	return imapmail


def filterInbox(imapmail,filterVariable,filterValue,mailbox="Inbox"):
	# returns all mails where filterVariable == filterValue
	imapmail.select(mailbox)
	result, data = imapmail.uid("search", None, "(HEADER " + filterVariable + " '" + filterValue + "')")
	id_list = data[0].split()
	if id_list:
		log("Mailbox: %i mail(s) in %s containing '%s' in '%s'." %(len(id_list),mailbox,filterValue,filterVariable),2)
		return id_list
	else:
		return []

def answerMails(imapmail,id_list,subject,text):
	for uid in id_list:
		result, data = imapmail.uid("fetch", uid, "(BODY[HEADER.FIELDS (FROM)])")
		client_mail_addr = data[0][1][data[0][1].find("<")+1:data[0][1].find(">")]
		if client_mail_addr == mail_address:
			log("Error: Tried to answer own mail. (uid %i, Subject '%s')"%(uid,subject))
		elif "noreply" in client_mail_addr:
			log("Error: Tried to answer automated. (uid %i, Subject '%s', address %s)"%(uid,subject,client_mail_addr))
		else:
			smtpMail(client_mail_addr,"Subject: %s\n\n%s"%(subject,text))
	return id_list

def moveMails(imapmail,id_list,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	for uid in id_list:
		# https://tools.ietf.org/html/rfc6851
		result,data = imapmail.uid("MOVE",uid,destination)
		if result == "OK":
			log("Moved uid%s to %s"%(uid,destination),2)
		else:
			log("Error moving uid%s to %s"%(uid,destination),1)


def smtpMail(to,what):
	smtpmail = smtplib.SMTP(smtpmail_server)
	smtpmail.ehlo()
	smtpmail.starttls()
	smtpmail.login(mail_address, mail_password)
	smtpmail.sendmail(mail_address, to, what)
	smtpmail.quit()


def log(what,level=2):
	if level<= log_level:
		print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + what)

if __name__ == "__main__":
	main()
