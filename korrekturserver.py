import tornado.ioloop
import tornado.web
import base64
import logging

import helper


class requestHandlerWithAuth(tornado.web.RequestHandler):
    def _execute(self, transforms, *args, **kwargs):
        # executed before everything else.
        if httpBasicAuth(self,kwargs):
            return tornado.web.RequestHandler._execute(self, transforms, *args, **kwargs)
        return False

class tableHandler(requestHandlerWithAuth):
    def get(self):
        self.write("Logged in.")


def main():
    helper.setupLogging()

    application = tornado.web.Application([
        (r"/",tableHandler),
    ])

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

    logging.debug("Server started.")

def httpBasicAuth(self,*kwargs):
    # http://de.wikipedia.org/wiki/HTTP-Statuscode
    receivedAuth = self.request.headers.get("Authorization")

    if receivedAuth is not None:
        decodedAuth = base64.decodestring(receivedAuth[6:])
        username, password = decodedAuth.split(":", 2)
        password = helper.md5sum(password)
        korrektoren = helper.getConfigValue("korrektoren")
        if korrektoren[username] == password:
            logging.debug("Received login from %s. Hi!"%username)
            return True
        logging.error("Failed login from %s with password %s."%(username,password))

    self.set_status(401)
    self.set_header("WWW-Authenticate", "Basic realm='netsec-Uebungssystem Korrektoranmeldung'")
    self._transforms = []
    self.write("401: Authentifizierung erforderlich.")
    self.finish()
    return False

if __name__ == "__main__":
    main()