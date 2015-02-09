import tornado.ioloop
import tornado.web
import base64
import logging
import os
from passlib.hash import pbkdf2_sha256

import helper


class requestHandlerWithAuth(tornado.web.RequestHandler):

    def _execute(self, transforms, *args, **kwargs):
        # executed before everything else.
        if httpBasicAuth(self, kwargs):
            return tornado.web.RequestHandler._execute(self, transforms, *args, **kwargs)
        return False


class tableHandler(requestHandlerWithAuth):

    def get(self, *args, **kwargs):
        if helper.getConfigValue("settings")["savemode"] == "file":
            abgaben = []
            if os.path.exists("attachments"):
                for entry in os.listdir("attachments/"):
                    abgaben.append(entry.lower())

            self.render("table.html", abgaben=abgaben)


class zipHandler(requestHandlerWithAuth):

    def get(self, *args, **kwargs):
        requestedFile = self.request.uri.replace("/zips/", "/zips").replace("/zips", "")

        if len(requestedFile) is 0:
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
        if not status:
            self.write(readStatus(student))
        else:
            writeStatus(student, status)


def main():
    helper.setupLogging()

    application = tornado.web.Application([
        (r"/", tableHandler),
        (r"/zips/.*", zipHandler),
        (r"/status/.*", statusHandler),
    ])

    logging.debug("Server started on port %i.", helper.getConfigValue("login")["korrektur_server_port"])

    application.listen(helper.getConfigValue("login")["korrektur_server_port"])
    tornado.ioloop.IOLoop.instance().start()


def httpBasicAuth(self, *kwargs):
    # http://de.wikipedia.org/wiki/HTTP-Statuscode
    receivedAuth = self.request.headers.get("Authorization")

    if receivedAuth is not None:
        decodedAuth = base64.decodestring(receivedAuth[6:])
        username, password = decodedAuth.split(":", 2)
        korrektoren = helper.getConfigValue("korrektoren")
        if username not in korrektoren:
            logging.debug("Received nonexistent user '%s'." % username)
            return False
        if pbkdf2_sha256.verify(password, korrektoren[username]):
            return True
        logging.error("Failed login from '%s' with password '%s'." % (username, password))

    self.set_status(401)
    self.set_header("WWW-Authenticate", "Basic realm='netsec-Uebungssystem Korrektoranmeldung'")
    self._transforms = []
    self.write("401: Authentifizierung erforderlich.")
    self.finish()
    return False


def readStatus(student):
    student = student.lower()

    retdir = os.getcwd()

    if not os.path.exists("attachments"):
        return
    os.chdir("attachments")

    if not os.path.exists(student):
        return "Student ohne Abgabe"
    os.chdir(student)

    if not os.path.exists("korrekturstatus.txt"):
        return "Unbearbeitet"
    statusfile = open("korrekturstatus.txt", "r")
    status = statusfile.read()
    statusfile.close()
    os.chdir(retdir)
    return status


def writeStatus(student, status):
    student = student.lower()
    status = status.lower()
    retdir = os.getcwd()

    if not os.path.exists("attachments"):
        return
    os.chdir("attachments")

    if not os.path.exists(student):
        return
    os.chdir(student)
    statusfile = open("korrekturstatus.txt", "w")
    statusfile.write(status)
    statusfile.close()
    os.chdir(retdir)

if __name__ == "__main__":
    main()
