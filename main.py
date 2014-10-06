from __future__ import unicode_literals
import imaplib
import smtplib
from time import sleep
import datetime

smtpmail_server   = "smtp.gmail.com"
imapmail_server   = "imap.gmail.com"

mail_address  = "netsec.imap.test@gmail.com"
mail_password = "tuxgit1337"

def login():
	imapmail = imaplib.IMAP4_SSL(imapmail_server)
	imapmail.login(mail_address,mail_password)
	imapmail.select()
	log("IMAP-Login auf %s mit %s erfolgreich."%(imapmail_server,mail_address))
	log("SMTP-Login auf %s mit %s erfolgreich."%(smtpmail_server,mail_address))

	return imapmail

def pollInbox(imapmail):
	imapmail.select()
	result,data = imapmail.uid("search",None,"(HEADER Subject 'Aufgabe')")
	id_list = data[0].split()
	if id_list:
		log("Maileingang: %i Mail(s) mit Betreff '*Aufgabe*' eingegangen"%len(id_list))
		for uid in id_list:
			# "Bewegen" existiert in IMAP nicht, also:
			# (1) Nachricht kopieren,
			# (2) Alte Nachricht loeschen.
			imapmail.uid("copy",uid,"Unbearbeitet")
			imapmail.uid("store",uid,"+FLAGS","(\Deleted)")
			imapmail.expunge()
			result,data = imapmail.uid("fetch",uid,"(BODY[HEADER.FIELDS (FROM)])")
			print(data)

def sendMail(to,template):
	smtpmail = smtplib.SMTP(smtpmail_server)
	smtpmail.ehlo()
	smtpmail.starttls()
	smtpmail.login(mail_address,mail_password)
	smtpmail.sendmail(mail_address,to,template)
	smtpmail.quit()

def log(what):
	print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + what)

def main():	
	imapmail = login()
	while(True):
		pollInbox(imapmail)
		sleep(3)

if __name__ == "__main__":
	main()
	#sendMail("martin.dessauer@uni-duesseldorf.de","Subject: Danke! E-Mail erhalten.\r\n\r\nIhre E-Mail ist eingegangen und wird bearbeitet.")
