from __future__ import unicode_literals
import sys

if not __package__:
    # direct call of korrekturserver.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))

import tornado.ioloop
import tornado.web
import base64
import logging
import os
import argparse
from passlib.hash import pbkdf2_sha256

from netsecus import helper
from netsecus import korrekturtools


class requestHandlerWithAuth(tornado.web.RequestHandler):

    def _execute(self, transforms, *args, **kwargs):
        # executed before everything else.
        if httpBasicAuth(self, kwargs):
            return tornado.web.RequestHandler._execute(self, transforms, *args, **kwargs)
        return False


class tableHandler(requestHandlerWithAuth):

    def get(self, *args, **kwargs):
        abgaben = []
        attachmentPath = helper.getConfigValue("settings", "attachment_path")
        if os.path.exists(attachmentPath):
            for entry in os.listdir(attachmentPath):
                if entry[0] != ".":
                    abgaben.append(entry.lower())
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        htmlPath = helper.getConfigValue("settings", "html_path")
        self.render(os.path.join("..", htmlPath, "table.html"), abgaben=abgaben)


class zipHandler(requestHandlerWithAuth):

    def get(self, *args, **kwargs):
        requestedFile = self.request.uri.replace("/zips/", "/zips").replace("/zips", "")

        if len(requestedFile) == 0:
            self.set_status(404)
            self.write("Zur&uuml;ck zur <a href=\"/\">&Uuml;bersicht</a>")
            self.finish()
            return

        self.write(requestedFile)


class statusHandler(requestHandlerWithAuth):

    def get(self, *args, **kwargs):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "-config", default="config.json",
                        help="Path to the config.json to be used", dest="configPath")
    args = vars(parser.parse_args())
    helper.configPath = args["configPath"]
    helper.setupLogging()

    application = tornado.web.Application([
        (r"/", tableHandler),
        (r"/zips/.*", zipHandler),
        (r"/status/.*", statusHandler),
    ])

    logging.debug("Server started on port %i.", helper.getConfigValue("login", "korrektur_server_port"))

    application.listen(helper.getConfigValue("login", "korrektur_server_port"))
    tornado.ioloop.IOLoop.instance().start()


def httpBasicAuth(self, *kwargs):
    # http://de.wikipedia.org/wiki/HTTP-Statuscode
    receivedAuth = self.request.headers.get("Authorization")

    if receivedAuth is not None:
        authMode, auth = receivedAuth.split(" ")
        if authMode != "Basic":
            logging.error("Used other HTTP authmode than 'Basic', '%s'." % authMode)
        else:
            username, password = base64.decodestring(auth).split(":", 2)
            korrektoren = helper.getConfigValue("korrektoren")
            if username not in korrektoren:
                logging.debug("Received nonexistent user '%s'." % username)
            elif not pbkdf2_sha256.verify(password, korrektoren[username]):
                logging.error("Failed login from '%s' with password '%s'." % (username, password))
            else:
                logging.debug("User '%s' logged in." % username)
                return self

    self.set_status(401)
    self.set_header("WWW-Authenticate", "Basic realm='netsec-Uebungssystem Korrektoranmeldung'")
    self._transforms = []
    self.write("401: Authentifizierung erforderlich.")
    self.finish()
    return self

if __name__ == "__main__":
    main()
