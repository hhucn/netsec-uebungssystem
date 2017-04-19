from __future__ import unicode_literals

import email.header
import email.mime.text

import time
import os.path
import logging
import smtplib


from .helper import MailProcessingError
from . import helper
from . import mail_helper
from . import template_helper


class Mailer(object):
    def __init__(self, config):
        self.config = config
        self.smtp_connect()

        try:
            username = config('mail.username')
        except KeyError:
            username = config('mail.address')
        self.imap = mail_helper.loginIMAP(
            config("mail.imap_server"),
            username,
            config("mail.password"),
            config("mail.ssl"),
            config("loglevel") == "debug")

    def send_template(self, to, subject, template, variables={}):
        template_path = os.path.join(self.config.module_path, "templates", template)

        if not os.path.exists(template_path):
            raise MailProcessingError("Template %s not found" % template_path)

        with open(template_path) as template_file:
            body = template_file.read()

        rendered_body = template_helper.render_template(body, variables)

        self.send(to, subject, rendered_body)

    def send(self, to, subject, body):
        msg = email.mime.text.MIMEText(body, 'html', 'utf-8')
        # TODO improve this encoding (only do MIME encoding when not only simple ASCII)
        msg['Subject'] = helper.encode_mail_words(subject)
        msg['To'] = helper.encode_mail_words(to)

        try:
            address = self.config("mail.username")
        except KeyError:
            address = self.config("mail.address")

        msg['From'] = helper.encode_mail_words("%s <%s>" % (self.config("mail.label"), address))
        mail = msg.as_string()
        self.smtp_send(to, mail)
        self.imap.append("Sent", "\Seen", time.localtime(), mail.encode("UTF-8"))

    def smtp_send(self, to, what):
        logging.debug('Sending mail to %s' % to)
        self.smtpmail.sendmail(self.config("mail.address"), to, what)

    def smtp_connect(self):
        try:
            username = self.config('mail.username')
        except KeyError:
            username = self.config('mail.address')

        self.smtpmail = smtplib.SMTP_SSL(self.config("mail.smtp_server"))
        self.smtpmail.ehlo()
        self.smtpmail.login(username, self.config("mail.password"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.smtpmail.quit()
        except Exception:
            pass

        try:
            mail_helper.logoutIMAP(self.imap)
        except Exception:
            pass


def send_template(config, *args, **kwargs):
    with Mailer(config) as mailer:
        mailer.send_template(*args, **kwargs)
