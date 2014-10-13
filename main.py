#!/usr/bin/env python

from __future__ import unicode_literals

import imaplib
import smtplib
from time import sleep
import datetime
import json
import os.path
import hashlib



#
# core functions
#

def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)
	
	# Parsing config.json, making the settings global
	global smtpmail_server,imapmail_server,mail_address,mail_password,loglevel,logmethod,delay
	configFile = json.load(open("config.json"))
	settings = configFile["settings"]
	rules = configFile["rules"]
	mail_address = settings["mail_address"]
	mail_password = settings["mail_password"]
	loglevel = settings["loglevel"]
	logmethod = settings["logmethod"]
	smtpmail_server = settings["smtpmail_server"]
	imapmail_server = settings["imapmail_server"]
	delay = settings["delay"]

	imapmail = login()
	while(True):
		for rule in rules:
			processRule(imapmail,rule)
			sleep(delay)

def login():
	imapmail = imaplib.IMAP4_SSL(imapmail_server)
	imapmail.login(mail_address, mail_password)
	imapmail.select()
	log("IMAP login (%s on %s)" % (mail_address,imapmail_server),3)

	return imapmail

def processRule(imapmail,rule):
	for step in rule["steps"]:
		if step[0] == "filter":
			id_list = filterMailbox(imapmail,step[1],step[2])
		elif step[0] == "answer":
			if len(step)>3:
				id_list = answerMails(imapmail,id_list,step[1],step[2],step[3])
			else:
				id_list = answerMails(imapmail,id_list,step[1],step[2],"")
		elif step[0] == "move":
			id_list = moveMails(imapmail,id_list,step[1])
		elif step[0] == "log":
			log(step[1],step[2])
		else:
			log("Rule <%s>, Step <%s>: step action unknown."%(rule["title"],step[0]),1)



#
# procession functions
#

def filterMailbox(imapmail,filterVariable,filterValue,mailbox="Inbox"):
	# returns all mails where filterVariable == filterValue
	# see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
	# and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
	imapmail.select(mailbox)
	result, data = imapmail.uid("search","ALL","*")
	uidlist = []
	if data != ['']:
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

def answerMails(imapmail,id_list,subject,text,address):
	# see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
	for uid in id_list:
		hashobj = hashlib.md5()
		hashobj.update(subject)
		subject_hash = hashobj.hexdigest()

		result, data = imapmail.uid("fetch", uid, "(BODY[HEADER.FIELDS (FROM)])")
		rawMail = data[0][1]
		if(address):
			client_mail_addr = address
		else:
			client_mail_addr = rawMail[rawMail.find("<")+1:rawMail.find(">")]

		if "NETSEC-Answered-" + subject_hash in imapmail.uid("fetch",uid,"FLAGS")[1][0]:
			log("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(uid,client_mail_addr,subject),3)
		else:
			if client_mail_addr == mail_address:
				log("Error: Tried to answer own mail. (uid %i, Subject '%s')"%(uid,subject),2)
			elif "noreply" in client_mail_addr:
				log("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(uid,client_mail_addr,subject),3)
			else:
				smtpMail(client_mail_addr,"Subject: %s\n\n%s"%(subject,text))
				imapmail.uid("STORE",uid,"+FLAGS","NETSEC-Answered-" + subject_hash)
	return id_list

def moveMails(imapmail,id_list,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	imapmail.create(destination)
	for uid in id_list:
		# https://tools.ietf.org/html/rfc6851
		result,data = imapmail.uid("MOVE",uid,destination)
		if result != "OK":
			log("Error moving uid%s to %s"%(uid,destination),1)



#
# helper functions
#

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