#!/usr/bin/env python

from __future__ import unicode_literals


import imaplib
import smtplib
import time
import json
import logging
import hashlib
import sys
from email.parser import Parser
import email
import sqlite3
import base64
import re

debug = True
# this may be used along with $ openssl s_client -crlf -connect imap.gmail.com:993


class mailContainer():
	imapmail = 0
	mails = []

	def __init__(self,imap,uid,temp):
		self.imapmail = imap
		self.uidlist = uid
		self.templates = temp

class mailElement():
	uid = -1
	templates = []
	rfc822 = ""

	def __init__(self,uid,templates,rfc822):
		self.uid = uid
		self.templates = templates
		self.rfc822 = rfc822

#
# core functions
#

def main():
	# patching imaplib
	imaplib.Commands["MOVE"] = ("SELECTED",)
	imaplib.Commands["IDLE"] = ("AUTH","SELECTED",)
	imaplib.Commands["DONE"] = ("AUTH","SELECTED",)

	# Parsing config.json, making the settings global
	global settings,templates
	configFile = json.load(open("config.json"))
	settings = configFile["settings"]
	templates = configFile["templates"]

	loglevel = settings.get("loglevel","ERROR")
	if loglevel == "ALL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.DEBUG)
	elif loglevel == "ERROR":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.ERROR)
	elif loglevel == "CRITICAL":
		logging.basicConfig(format="%(asctime)s %(message)s",level=logging.CRITICAL)

	rules = configFile["rules"]

	imapmail = login()
	imapmail._command("IDLE")
	

	if "idling" in imapmail.readline():
		logging.debug("Server supports IDLE.")

		# to process mails which already resists in the Inbox
		imapmail._command("DONE")
		imapmail.readline()

		for rule in rules:
			processRule(mailContainer(imapmail,[],templates),rule["steps"])

		imapmail._command("IDLE")

		while(True):
			if "EXISTS" in imapmail.readline():
				imapmail._command("DONE")
				imapmail.readline()
				processRule(mailContainer(imapmail,[],templates),rule["steps"])
				imapmail._command("IDLE")
	else:
		logging.debug("Server lacks support for IDLE... Falling back to delay.")
		while(True):
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

def processRule(mailcontainer,rule):
	if debug:
		print "**** rule"
	for step in rule:
		if debug:
			print "exec: " + step[0]
		mailcontainer = getattr(sys.modules[__name__],"rule_" + step[0])(mailcontainer,*step[1:])
		if not mailcontainer.uidlist:
			break
		if debug:
			print " ret: " + ",".join(mailcontainer.uidlist)
	if debug:
		print "**** done\n"



#
# rule functions
#

def rule_filter(mailcontainer,filterVariable,filterValue,mailbox="INBOX"):
	# returns all mails where filterVariable == filterValue

	# see http://tools.ietf.org/html/rfc3501#section-6.4.4 (for search)
	# and http://tools.ietf.org/html/rfc3501#section-6.4.5 (for fetch)
	mailcontainer.imapmail.select(mailbox)

	data = imapCommand(mailcontainer.imapmail,"search","ALL","*")
	if data != ['']:
		if filterVariable == "ALL":
			return data
		
		for uid in data:
			if uid:
				data = imapCommand(mailcontainer.imapmail,"fetch",uid,"(BODY[HEADER])")
				header = Parser().parsestr(data[0][1])
				if filterValue.upper() in header[filterVariable].upper():
					mailcontainer.uidlist.append(uid)
					print mailcontainer.uidlist
	return mailcontainer

def rule_answer(mailcontainer,subject,text,address="(back)"):
	# see http://tools.ietf.org/html/rfc3501#section-6.4.6 (for store)
	for uid in mailcontainer.uidlist:
		hashobj = hashlib.md5()
		hashobj.update(subject + text)
		subject_hash = hashobj.hexdigest()

		data = imapCommand(mailcontainer.imapmail,"fetch", uid, "(BODY[HEADER.FIELDS (FROM)])")
		rawMail = data[0][1]
		if address == "(back)":
			client_mail_addr = re.findall("\<[^ ]*\>",rawMail)[0]
		else:
			client_mail_addr = address
		
		if "NETSEC-Answered-" + subject_hash in imapCommand(mailcontainer.imapmail,"fetch",uid,"FLAGS"):
			logging.error("Error: Tried to answer to mail (uid %s, addr '%s', Subject '%s') which was already answered."%(uid,client_mail_addr,subject))
		else:
			if "noreply" in client_mail_addr:
				logging.error("Error: Tried to answer automated mail. (uid %i, addr '%s' Subject '%s')"%(uid,client_mail_addr,subject))
			else:
				smtpMail(client_mail_addr,"Content-Type:text/html\nSubject: %s\n\n%s"%(checkForTemplate(subject),checkForTemplate(text)))
				rule_flag(mailContainer(mailcontainer.imapmail,[uid],[]),"NETSEC-Answered-" + subject_hash)
	return mailcontainer

def rule_move(mailcontainer,destination):
	# moves the mails from id_list to mailbox destination
	# warning: this alters the UID of the mails!
	mailcontainer.imapmail.create(destination)
	for uid in mailcontainer.uidlist:
		# https://tools.ietf.org/html/rfc6851
		data = imapCommand(mailcontainer.imapmail,"MOVE",uid,destination)
	mailcontainer.uidlist = []
	return mailcontainer

def rule_flag(mailcontainer,flag):
	for uid in mailcontainer.uidlist:
		imapCommand(mailcontainer.imapmail,"STORE",uid,"+FLAGS",flag.replace("\\","\\\\")) # could interpret \NETSEC as <newline>ETSEC
	return mailcontainer

def rule_log(mailcontainer,lvl,msg):
	if lvl == "LOG":
		logging.debug(msg)
	else:
		logging.error(msg)
	return mailcontainer

def rule_delete(mailcontainer):
	rule_flag(mailcontainer.imapmail,"DELETE")
	mailcontainer.imapmail.expunge()
	return mailcontainer

def rule_save(mailcontainer,withAttachment="True"):
	sqldatabase = sqlite3.connect(settings.get("database"))
	cursor = sqldatabase.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS inbox (addr text,date text,subject text,korrektor text,attachment blob)")

	for uid in mailcontainer.uidlist:
		data = imapCommand(mailcontainer.imapmail,"fetch",uid,"(RFC822)")
		mail = Parser().parsestr(data[0][1])
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
	return mailcontainer

#
# helper functions
#

def checkForTemplate(raw):
	varInRaw = re.findall("\$([A-Z]*)",raw)
	if varInRaw:
		for var in varInRaw:
			if var in templates:
				raw = raw.replace("$" + var,checkForTemplate(templates.get(var)))
	return raw

def imapCommand(imapmail,command,uid,*args):
	if debug:
		print "\t" + command + " " + uid + " " + " ".join(args)

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

if __name__ == "__main__":
	main()