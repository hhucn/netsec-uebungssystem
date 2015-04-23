from __future__ import unicode_literals

import base64
import logging
import os

import tornado.ioloop
import tornado.web
from passlib.hash import pbkdf2_sha256

from . import korrekturtools


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
                korrektoren = self.application.config("korrektoren")
                if username not in korrektoren:
                    logging.debug("Received nonexistent user '%s'." % username)
                elif not pbkdf2_sha256.verify(password, korrektoren[username]):
                    logging.error("Failed login for %s from %s." % (username, self.request.remote_ip))
                else:
                    logging.debug("User '%s' logged in." % username)
                    return super(RequestHandlerWithAuth, self)._execute(transforms, *args, **kwargs)

        self.set_status(401)
        self.set_header("WWW-Authenticate", "Basic realm='netsec-Uebungssystem Korrektoranmeldung'")
        self._transforms = []
        self.write("401: Authentifizierung erforderlich.")
        self.finish()


class TableHandler(RequestHandlerWithAuth):
    def get(self):
        abgaben = []
        attachmentPath = self.application.config("attachment_path")
        if os.path.exists(attachmentPath):
            for entry in os.listdir(attachmentPath):
                if entry[0] != ".":
                    abgaben.append(entry.lower())
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        htmlPath = self.application.config("html_path")
        self.render(os.path.join("..", htmlPath, "table.html"), abgaben=abgaben)


class ZipHandler(RequestHandlerWithAuth):
    def get(self):
        requestedFile = self.request.uri.replace("/zips/", "/zips").replace("/zips", "")

        if len(requestedFile) == 0:
            self.set_status(404)
            self.write("Zur&uuml;ck zur <a href=\"/\">&Uuml;bersicht</a>")
            self.finish()
            return

        self.write(requestedFile)


class StatusHandler(RequestHandlerWithAuth):
    def get(self):
        uri = self.request.uri.replace("/status/", "")
        if uri.count("/") == 1:
            student, status = uri.split("/")
        else:
            student = uri
            status = ""
        if status:
            korrekturtools.writeStatus(student, status)
        else:
            self.write(korrekturtools.readStatus(student))


class KorrekturApp(tornado.web.Application):
    def __init__(self, config, handlers):
        super(KorrekturApp, self).__init__(handlers)
        self.config = config


def mainloop(config):
    application = KorrekturApp(config, [
        (r"/", TableHandler),
        (r"/zips/.*", ZipHandler),
        (r"/status/.*", StatusHandler),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
