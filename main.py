#!/usr/bin/env python

from __future__ import unicode_literals

import imaplib
import smtplib
from time import sleep
import datetime
import json
import os.path


def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)
	
	# Parsing config.ini, making the settings global
	global smtpmail_server,imapmail_server,mail_address,mail_password,loglevel,logmethod,delay
	configFile = json.load(open("config.json"))
	mail_address = configFile["settings"]["mail_address"]
	mail_password = configFile["settings"]["mail_password"]
	loglevel = configFile["settings"]["loglevel"]
	logmethod = configFile["settings"]["logmethod"]
	smtpmail_server = configFile["settings"]["smtpmail_server"]
	imapmail_server = configFile["settings"]["imapmail_server"]
	delay = configFile["settings"]["delay"]

	imapmail = login()
	while(True):
		# nesting, like in jQuery, are possible because the functions return an id_list.
		# moveMails(imapmail,answerMails(imapmail,filterMailbox(imapmail,"Subject","Aufgabe","Inbox"),"Mail eingegangen","Ihre E-Mail ist eingegangen"),"Unbearbeitet")
		# for debugging reasons (and because it's not really beautiful code), it should be used like this:
		id_list = filterMailbox(imapmail,"Subject","Aufgabe")
		answerMails(imapmail,id_list,"Mail eingegangen!","Ihre Mail ist eingegangen und wird beantwortet, da sie 'Aufgabe' im Titel traegt. Yay :3")
		moveMails(imapmail,id_list,"Aufgabencontainer")

		id_list = filterMailbox(imapmail,"Subject","Frage")
		answerMails(imapmail,id_list,"Frage eingegangen!","Ihre Frage ist eingegangen und wird beantwortet.")
		moveMails(imapmail,id_list,"Fragencontainer")
		sleep(delay)

def login():
	imapmail = imaplib.IMAP4_SSL(imapmail_server)
	imapmail.login(mail_address, mail_password)
	imapmail.select()
	log("IMAP login (%s on %s)" % (mail_address,imapmail_server),3)

	return imapmail




def filterMailbox(imapmail,filterVariable,filterValue,mailbox="Inbox"):
	# returns all mails where filterVariable == filterValue
	# see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
	# and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
	imapmail.select(mailbox)
	result, data = imapmail.uid("search","ALL","*")
	uidlist = []
	if data is not '':
		for uid in data:
			if uid:
				result,data = imapmail.uid("fetch",uid,"(BODY[HEADER])")
				headerList = []
				header = {}
				for line in data[0][1].split("\r\n"):
					if ": " in line:
						headerList.append(line)
					else:
						headerList[-1] += line
				for line in headerList:
					split = line.split(": ",1)
					header[split[0]] = split[1]
				if filterValue.upper() in header[filterVariable].upper():
					uidlist.append(uid)
	return uidlist




def answerMails(imapmail,id_list,subject,text):
	# see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
	for uid in id_list:
		if "NETSEC-Answered" in imapmail.uid("fetch",uid,"FLAGS")[1][0]:
			log("Error: Tried to answer to mail (uid %s) which was already answered."%uid,2)
		else:
			result, data = imapmail.uid("fetch", uid, "(BODY[HEADER.FIELDS (FROM)])")
			client_mail_addr = data[0][1][data[0][1].find("<")+1:data[0][1].find(">")]
			if client_mail_addr == mail_address:
				log("Error: Tried to answer own mail. (uid %i, Subject '%s')"%(uid,subject),2)
			elif "noreply" in client_mail_addr:
				log("Error: Tried to answer automated. (uid %i, Subject '%s', address %s)"%(uid,subject,client_mail_addr),2)
			else:
				smtpMail(client_mail_addr,"Subject: %s\n\n%s"%(subject,text))
				imapmail.uid("STORE",uid,"+FLAGS","NETSEC-Answered")
	return id_list

def moveMails(imapmail,id_list,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	imapmail.create(destination)
	for uid in id_list:
		# https://tools.ietf.org/html/rfc6851
		result,data = imapmail.uid("MOVE",uid,destination)
		if result == "OK":
			log("Moved uid%s to %s"%(uid,destination),3)
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
	if level<= loglevel:
		logString = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + what

		if logmethod==1 or logmethod==3:
			print(logString)
		if logmethod==2 or logmethod==3:
			logfile = open("logfile.log","a")
			logfile.write(logString + "\n")
			logfile.close()
if __name__ == "__main__":
	main()
