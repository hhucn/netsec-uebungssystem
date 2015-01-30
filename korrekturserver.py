import tornado.ioloop
import tornado.web
import base64
import logging
import os

import helper


class requestHandlerWithAuth(tornado.web.RequestHandler):
    def _execute(self, transforms, *args, **kwargs):
        # executed before everything else.
        if httpBasicAuth(self,kwargs):
            return tornado.web.RequestHandler._execute(self, transforms, *args, **kwargs)
        return False

class tableHandler(requestHandlerWithAuth):
    def get(self):
        if helper.getConfigValue("settings")["savemode"] == "file":
            studenten = []
            if os.path.exists("attachments"):
                for entry in os.listdir("attachments/"):
                   studenten.append(entry)

            self.write("<ul>")
            for student in studenten:
                self.write("<li>")
                self.write(student)
                self.write("</li>")
            self.write("</ul>")

def main():
    helper.setupLogging()

    application = tornado.web.Application([
        (r"/",tableHandler),
    ])

    logging.debug("Server started on port %i.",helper.getConfigValue("login")["korrektur_server_port"])

    application.listen(helper.getConfigValue("login")["korrektur_server_port"])
    tornado.ioloop.IOLoop.instance().start()

def httpBasicAuth(self,*kwargs):
    # http://de.wikipedia.org/wiki/HTTP-Statuscode
    receivedAuth = self.request.headers.get("Authorization")

    if receivedAuth is not None:
        decodedAuth = base64.decodestring(receivedAuth[6:])
        username, password = decodedAuth.split(":", 2)
        password = helper.md5sum(password)
        korrektoren = helper.getConfigValue("korrektoren")
        if username not in korrektoren:
            logging.debug("Received nonexistent user '%s'."%username)
            return False
        if korrektoren[username] == password:
            return True
        logging.error("Failed login from '%s' with password '%s'."%(username,password))

    self.set_status(401)
    self.set_header("WWW-Authenticate", "Basic realm='netsec-Uebungssystem Korrektoranmeldung'")
    self._transforms = []
    self.write("401: Authentifizierung erforderlich.")
    self.finish()
    return False

if __name__ == "__main__":
    main()