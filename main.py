#!/usr/bin/env python

from __future__ import unicode_literals

import imaplib
import smtplib
from time import sleep
import datetime
import json
import os
import hashlib
from sys import exit



#
# core functions
#

def main():
	# patching imaplib
	imaplib.Commands["MOVE"]=("SELECTED",)
	
	# Parsing config.json, making the settings global
	global smtpmail_server,imapmail_server,mail_address,mail_password,loglevel,logmethod,delay
	
	if not os.path.isfile("config.json"):
		log("'config.json' doesn't exist.",1)

	configFile = json.load(open("config.json"))
	settings = loadConfigElement(configFile,"settings")
	rules = configFile["rules"]
	mail_address = loadConfigElement(settings,"mail_address")
	mail_password = loadConfigElement(settings,"mail_password")
	loglevel = loadConfigElement(settings,"loglevel")
	logmethod = loadConfigElement(settings,"logmethod")
	smtpmail_server = loadConfigElement(settings,"smtpmail_server")
	imapmail_server = loadConfigElement(settings,"imapmail_server")
	delay = loadConfigElement(settings,"delay")

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
		action = step[0]
		steplen = len(step)
		if action == "filter":
			if steplen==3:
				id_list = filterMailbox(imapmail,step[1],step[2])
			elif steplen==4:
				id_list = filterMailbox(imapmail,step[1],step[2],step[3])
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		elif action == "answer":
			if steplen==4:
				id_list = answerMails(imapmail,id_list,step[1],step[2],step[3])
			elif steplen==3:
				id_list = answerMails(imapmail,id_list,step[1],step[2],"")
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		elif action == "move":
			if steplen==2:
				id_list = moveMails(imapmail,id_list,step[1])
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		elif action == "log":
			if steplen==3:
				log(step[1],step[2])
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		elif action == "flag":
			if steplen==2:
				id_list = flagMails(imapmail,id_list,step[1])
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		elif action == "delete":
			if steplen==1:
				flagMails(imapmail,id_list,"\\Deleted")
				imapmail.expunge()
			else:
				log("Rule <%s>, Step <%s>: wrong argument count."%(rule["title"],action),1)
		else:
			log("Rule <%s>, Step <%s>: step action unknown."%(rule["title"],action),1)



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
			log("Error moving uid%s to %s"%(uid,destination),1)

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

def log(what,level=2):
	level = int(level)

	try:
		logmethod
	except NameError:
		logmethod = 3
	try:
		loglevel
	except NameError:
		loglevel = 3

	if level<= loglevel:
		logString = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":\t" + what

		if logmethod==1 or logmethod==3:
			print(logString)
		if logmethod==2 or logmethod==3:
			logfile = open("logfile.log","a")
			logfile.write(logString + "\n")
			logfile.close()
	if level == 1:
		print("\t\t\tReceived level 1 error message, shutting down server...")
		exit(-1)

def loadConfigElement(config,what):
	global loglevel, logmethod

	if what in config:
		return config[what]
	else:
		log("Important variable <" + what + "> is not assigned in config.json",1)

if __name__ == "__main__":
	main()