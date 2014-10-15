#!/usr/bin/env python

from __future__ import unicode_literals

import imaplib
import smtplib
from time import sleep
import datetime
from json import load as jsonLoad
import hashlib
from sys import exit
import logging



#
# core functions
#

def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)

	# Parsing config.json, making the settings global
	global smtpmail_server,imapmail_server,mail_address,mail_password,loglevel,logmethod,delay
	
	
	configFile = jsonLoad(open("config.json"))
	settings = configFile["settings"]

	#logging.basicConfig(format="%(asctime)s %(message)s")
	loglevel = settings.get("loglevel","ERROR")
	if loglevel == "ALL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.DEBUG)
	elif loglevel == "ERROR":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.ERROR)
	elif loglevel == "CRITICAL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.CRITICAL)

	rules = configFile["rules"]

	mail_address = settings.get("mail_address")
	mail_password = settings.get("mail_password")
	smtpmail_server = settings.get("smtpmail_server")
	imapmail_server = settings.get("imapmail_server")
	delay = settings.get("delay")

	imapmail = login()
	while(True):
		for rule in rules:
			processRule(imapmail,rule)
		sleep(delay)

def login():
	imapmail = imaplib.IMAP4_SSL(imapmail_server)
	imapmail.login(mail_address, mail_password)
	imapmail.select()
	logging.info("IMAP login (%s on %s)" % (mail_address,imapmail_server))

	return imapmail

def processRule(imapmail,rule):
	for step in rule["steps"]:
		action = step[0]
		steplen = len(step)
		if action == "filter":
			if steplen==3:
				id_list = filterMailbox(imapmail,step[1],step[2])
			elif steplen==4:
				id_list = filterMailbox(imapmail,step[1],step[2],step[3])
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		elif action == "answer":
			if steplen==4:
				id_list = answerMails(imapmail,id_list,step[1],step[2],step[3])
			elif steplen==3:
				id_list = answerMails(imapmail,id_list,step[1],step[2],"")
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		elif action == "move":
			if steplen==2:
				id_list = moveMails(imapmail,id_list,step[1])
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		elif action == "log":
			if steplen==3:
				if step[1] == "ERROR":
					logging.error(step[2])
				elif step[1] == "CRITICAL":
					logging.critical(step[2])
				else:
					logging.info(step[2])
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		elif action == "flag":
			if steplen==2:
				id_list = flagMails(imapmail,id_list,step[1])
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		elif action == "delete":
			if steplen==1:
				flagMails(imapmail,id_list,"\\Deleted")
				imapmail.expunge()
			else:
				logging.critical("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action))
				sys.exit(2)
		else:
			logging.critical("Rule <%s>, Step <%s>: step is unknown."%(rule["title"],action))
			sys.exit(2)



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
			logging.error("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(uid,client_mail_addr,subject))
		else:
			if client_mail_addr == mail_address:
				logging.error("Error: Tried to answer own mail. (uid %i, Subject '%s')"%(uid,subject))
			elif "noreply" in client_mail_addr:
				logging.error("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(uid,client_mail_addr,subject))
			else:
				smtpMail(client_mail_addr,"Subject: %s\n\n%s"%(subject,text))
				flagMails(imapmail,uid,"NETSEC-Answered-" + subject_hash)
				#imapmail.uid("STORE",uid,"+FLAGS","NETSEC-Answered-" + subject_hash)
	return id_list

def moveMails(imapmail,id_list,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	imapmail.create(destination)
	for uid in id_list:
		# https://tools.ietf.org/html/rfc6851
		result,data = imapmail.uid("MOVE",uid,destination)
		if result != "OK":
			logging.error("Error moving uid%s to %s"%(uid,destination))

def flagMails(imapmail,id_list,flag):
	for uid in id_list:
		imapmail.uid("STORE",uid,"+FLAGS",flag)
	return id_list


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

if __name__ == "__main__":
	main()