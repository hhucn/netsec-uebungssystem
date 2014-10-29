#!/usr/bin/env python

from __future__ import unicode_literals

import __imaplib as imaplib
import smtplib
import time
import datetime
import json
import hashlib
import sys
import logging



#
# core functions
#

def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)

	# Parsing config.json, making the settings global
	global settings
	
	
	configFile = json.load(open("config.json"))
	settings = configFile["settings"]

	loglevel = settings.get("loglevel","ERROR")
	if loglevel == "ALL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.DEBUG)
	elif loglevel == "ERROR":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.ERROR)
	elif loglevel == "CRITICAL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.CRITICAL)

	rules = configFile["rules"]

	imapmail = login()
	imapmail.select("INBOX")

	imapmail.send("%s IDLE\r\n"%imapmail._new_tag())

	if "idling" in imapmail.readline():
		logging.debug("Server supports IDLE.")

		# to process mails which already resists in the Inbox
		imapmail.send("DONE\r\n")
		imapmail.readline()

		for rule in rules:
			processRule(imapmail,rule["steps"])

		imapmail.send("%s IDLE\r\n"%imapmail._new_tag())

		while(True):
			if "EXISTS" in imapmail.readline():
				imapmail.send("DONE\r\n")
				imapmail.readline()

				for rule in rules:
					processRule(imapmail,rule["steps"])
				imapmail.send("%s IDLE\r\n"%imapmail._new_tag())
	else:
		logging.debug("Server lacks support for IDLE... Falling back to delay.")
		while(True):
			for rule in rules:
				processRule(imapmail,rule["steps"])
			time.sleep(settings.get("delay"))

def login():
	imapmail = imaplib.IMAP4_SSL(settings.get("imapmail_server"))
	imapmail.login(settings.get("mail_address"), settings.get("mail_password"))
	imapmail.select()
	logging.info("IMAP login (%s on %s)" % (settings.get("mail_address"),settings.get("imapmail_server")))

	return imapmail

def smtpMail(to,what):
	smtpmail = smtplib.SMTP(settings.get("smtpmail_server"))
	smtpmail.ehlo()
	smtpmail.starttls()
	smtpmail.login(settings.get("mail_address"), settings.get("mail_password"))
	smtpmail.sendmail(settings.get("mail_address"), to, what)
	smtpmail.quit()

def processRule(imapmail,rule):
	id_list = []
	for step in rule:
		print "\tstep %s type %s"%(step,type(id_list).__name__)
		id_list = globals()["rule_" + step[0]](imapmail,id_list,*step[1:])
		# if type(id_list).__name__ == "String":
		# 	print "woop"
		# 	print id_list
		# 	id_list = [id_list]


#
# procession functions
#

def rule_filter(imapmail,id_list,filterVariable,filterValue,mailbox="INBOX"):
	# returns all mails where filterVariable == filterValue
	# see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
	# and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
	imapmail.select(mailbox)

	data = imapCommand(imapmail,"search","ALL","*")
	uidlist = []
	if data != ['']:
		for uid in data:
			if uid:
				data = imapCommand(imapmail,"fetch",uid,"(BODY[HEADER])")
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

def rule_answer(imapmail,id_list,subject,text,address="(back)"):
	# see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
	for uid in id_list:
		hashobj = hashlib.md5()
		hashobj.update(subject)
		subject_hash = hashobj.hexdigest()

		data = imapCommand(imapmail,"fetch", uid, "(BODY[HEADER.FIELDS (FROM)])")
		rawMail = data[0][1]
		if address == "(back)":
			client_mail_addr = rawMail[rawMail.find("<")+1:rawMail.find(">")]
		else:
			client_mail_addr = address
		
		if "NETSEC-Answered-" + subject_hash in imapCommand(imapmail,"fetch",uid,"FLAGS"):
			logging.error("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(uid,client_mail_addr,subject))
		else:
			if client_mail_addr == settings.get("mail_password"):
				logging.error("Error: Tried to answer own mail. (uid %i, Subject '%s')"%(uid,subject))
			elif "noreply" in client_mail_addr:
				logging.error("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(uid,client_mail_addr,subject))
			else:
				smtpMail(client_mail_addr,"Subject: %s\n\n%s"%(subject,text))
				rule_flag(imapmail,uid,"NETSEC-Answered-" + subject_hash)
				imapCommand(imapmail,"STORE",uid,"+FLAGS","NETSEC-Answered-" + subject_hash)
	return id_list

def rule_move(imapmail,id_list,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	imapmail.create(destination)
	for uid in id_list:
		# https://tools.ietf.org/html/rfc6851
		data = imapCommand(imapmail,"MOVE",uid,destination)

def rule_flag(imapmail,id_list,flag):
	for uid in id_list:
		imapCommand(imapmail,"STORE",uid,"+FLAGS",flag)
	return id_list

def rule_log(imapmail,id_list,lvl,msg):
	if lvl == "LOG":
		logging.debug(msg)
	else:
		logging.error(msg)
	return id_list

def rule_delete(imapmail,id_list):
	rule_flag(imapmail,id_list,"\DELETE")
	imapmail.expunge()
	return id_list

#
# helper functions
#

def imapCommand(imapmail,command,uid,*args):
	#print "%s %s %s"%(command,uid,args)

	print "\t\ttype %s"%(type(uid).__name__)

	code, ids = imapmail.uid(command, uid, *args)

	if "OK" in code:
		return ids
	else:
		logging.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
		raise self.error("Server responded with Code '%s' for '%s %s %s'."%(code,command,uid,args))
		return []

if __name__ == "__main__":
	main()