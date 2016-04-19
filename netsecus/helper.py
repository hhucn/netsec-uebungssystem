from __future__ import unicode_literals, print_function

import base64
import email
import imaplib
import logging
import re
import smtplib
import sys

import tornado.web


def processVariable(variables, text):
    return re.sub(r'\$([a-zA-Z0-9_]+)',
                  lambda m: processVariable(variables, str(variables[m.group(0)])),
                  text)


def imapCommand(imapmail, command, *args):
    logging.debug("\t%s %s" % (command, " ".join(args)))

    args = [a.encode('utf-8') for a in args]

    typ, dat = imapmail._simple_command(command, *args)

    if command == "UID":
        command = args[0]

    code, response = imapmail._untagged_response(typ, dat, command)
    response = response[0]  # the response ships within a list with one element; we need to unpack that.

    if "OK" in code:
        return response
    else:
        err = "Server responded with Code '%s' for '%s %s'." % (code, command, args)
        raise MailConnectionError(err)


def uidCommand(imapmail, command, *args):
    logging.debug("\tUID %s %s" % (command, " ".join(args)))

    args = [a.encode('utf-8') for a in args]

    code, response = imapmail.uid(command, *args)

    if code == 'OK':
        return response[0]
    else:
        err = "Server responded with Code '%s' for '%s %s'." % (code, command, args)
        raise MailConnectionError(err)


def smtpMail(config, to, what):
    try:
        username = config('mail.username')
    except KeyError:
        username = config('mail.address')

    smtpmail = smtplib.SMTP_SSL(config("mail.smtp_server"))
    smtpmail.ehlo()
    smtpmail.login(username, config("mail.password"))
    smtpmail.sendmail(config("mail.address"), to, what)
    smtpmail.quit()


def patch_imaplib():
    # imaplib is missing some essential commands.
    # Since we just need these passed through to the server, patch them in
    imaplib.Commands["MOVE"] = ("SELECTED",)
    imaplib.Commands["IDLE"] = ("AUTH", "SELECTED",)
    imaplib.Commands["DONE"] = ("AUTH", "SELECTED",)
    imaplib.Commands["ENABLE"] = ("AUTH",)
    imaplib.Commands["CABABILITY"] = ("AUTH",)

    if sys.version_info < (3, 0):
        imaplib.IMAP4_SSL.send = imaplibSendPatch


def imaplibSendPatch(self, data):
    data = data.encode("utf-8")

    bytes = len(data)
    while bytes > 0:
        sent = self.sslobj.write(data)
        if sent == bytes:
            break    # avoid copy
        data = data[sent:]
        bytes = bytes - sent


def escape_filename(fn):
    assert isinstance(fn, str)
    fn = re.sub(r'[^a-zA-Z 0-9._-]', '_', fn)
    fn = re.sub(r'^\.', '_', fn)
    if not fn:
        fn = '_'

    assert re.match(r'^[a-zA-Z 0-9_-][a-zA-Z 0-9._-]*$', fn)
    return fn


def checkResult(imapmail, expected):
    # [1] Answer token "*": http://tools.ietf.org/html/rfc3501#section-2.2.2
    assert isinstance(expected, bytes)

    line = imapmail.readline()
    if not re.match(b"^(?:[A-Z0-9]{5,9}|[*])\s+" + expected, line):
        raise MailConnectionError("Invalid response: '%s' expected, but got '%s'" % (expected, line))


class RequestHandlerWithAuth(tornado.web.RequestHandler):
    def _execute(self, transforms, *args, **kwargs):
        # executed before everything else.
        receivedAuth = self.request.headers.get("Authorization")

        if receivedAuth is not None:
            authMode, auth_b64 = receivedAuth.split(" ")
            if authMode != "Basic":
                logging.error("Used other HTTP authmode than 'Basic', '%s'." % authMode)
            else:
                auth = base64.b64decode(auth_b64.encode('ascii'))
                username_b, _, password_b = auth.partition(b":")
                username = username_b.decode('utf-8')
                password = password_b.decode('utf-8')
                users = self.application.users

                from passlib.hash import pbkdf2_sha256
                if username not in users:
                    logging.debug("Received nonexistent user '%s'." % username)
                elif not pbkdf2_sha256.verify(password, users[username]):
                    logging.error("Failed login for %s from %s." % (username, self.request.remote_ip))
                else:
                    return super(RequestHandlerWithAuth, self)._execute(transforms, *args, **kwargs)

        self.set_status(401)
        realm = getattr(self.application, 'realm', '')
        self.set_header("WWW-Authenticate", "Basic realm=\"%s\"" % realm)
        self._transforms = []
        self.write("401: Authentifizierung erforderlich.")
        self.finish()


def create_imap_conn(server, ssl, debug):
    if ssl:
        res = imaplib.IMAP4_SSL(server)
    else:
        res = imaplib.IMAP4(server)
    if debug:
        send_func = res.send
        read_func = res.read
        readline_func = res.readline

        def _debug_send(data):
            print('> %s' % data.decode('utf-8'), end='')
            return send_func(data)

        def _debug_read(size):
            res = read_func(size)
            print('< %s' % res.decode('utf-8'), end='')
            return res

        def _debug_readline():
            res = readline_func()
            print('< %s' % res.decode('utf-8'), end='')
            return res

        res.send = _debug_send
        res.read = _debug_read
        res.readline = _debug_readline

    return res


# An error with the IMAP connection (interrupted, erorr message, etc.)
class MailConnectionError(BaseException):
    pass


# An error in handling a specific mail
class MailError(BaseException):
    def __init__(self, uid, msg):
        super().__init__(msg)
        self.uid = uid


# An error unrelated to a specific mail rather than the processing itself
class MailProcessingError(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


def setup_logging(config):
    loglevel = getattr(logging, config("loglevel").upper())
    logfile = config('logfile')

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(loglevel)

    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    root_logger.addHandler(stderr_handler)


def get_header(message, key, default=''):
    """ Get a header value as a string from an email message """
    raw_val = message.get(key, default)

    return ''.join(
        word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
        for word, encoding in email.header.decode_header(raw_val))
