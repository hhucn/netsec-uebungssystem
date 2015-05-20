from __future__ import unicode_literals

import logging
import os
from datetime import datetime

import tornado.ioloop
import tornado.web

from . import helper
from . import korrekturtools


class NetsecHandler(helper.RequestHandlerWithAuth):
    def render(self, template, data):
        htmlPath = self.application.config("html_path")
        super(NetsecHandler, self).render(
            os.path.join("..", htmlPath, "%s.html" % template),
            **data)


class TableHandler(NetsecHandler):
    def get(self):
        abgaben = []
        attachmentPath = self.application.config("attachment_path")
        if os.path.exists(attachmentPath):
            for entry in os.listdir(attachmentPath):
                if entry[0] != ".":
                    abgaben.append({
                        "name": entry.lower(),
                        "status": korrekturtools.readStatus(self.config, entry.lower())
                        })
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        self.render('table', {'reihen': abgaben})


class ZipHandler(NetsecHandler):
    def get(self):
        requestedFile = self.request.uri.replace("/zips/", "/zips").replace("/zips", "")

        if len(requestedFile) == 0:
            self.set_status(404)
            self.write("Zur&uuml;ck zur <a href=\"/\">&Uuml;bersicht</a>")
            self.finish()
            return

        self.write(requestedFile)


class StatusHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.replace("/status/", "")
        if uri.count("/") == 1:
            student, status = uri.split("/")
        else:
            student = uri
            status = ""
        if status:
            korrekturtools.writeStatus(self.config, student, status)
        else:
            self.write(korrekturtools.readStatus(self.config, student))


class DetailHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        uri = uri[2:][0]  # remove empty element and "detail", get student ID

        files = []
        mailtext = ""
        attachmentPath = self.application.config("attachment_path")
        if os.path.exists(attachmentPath):
            studentAttachmentPath = os.path.join(attachmentPath, helper.escapePath(uri))
            for entry in os.listdir(studentAttachmentPath):
                if entry == "mailtext.txt":
                    mailtext = "Mailtexttest"
                elif entry[0] != ".":
                    timestamp, name = entry.split(" ", 1)
                    files.append({
                        "name": name,
                        "size": "%s KB" % str(os.path.getsize(os.path.join(studentAttachmentPath, entry)) / 1024),
                        "date": datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d %H-%M")
                        })
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        self.render('detail', {'identifier': uri, 'files': files, 'mailtext': mailtext})


class KorrekturApp(tornado.web.Application):
    realm = 'netsec Uebungsabgabesystem'

    def __init__(self, config, handlers):
        super(KorrekturApp, self).__init__(handlers)
        for handler in handlers:
            handler[1].config = config
        self.config = config

    @property
    def users(self):
        return self.config('korrektoren')


def mainloop(config):
    application = KorrekturApp(config, [
        (r"/", TableHandler),
        (r"/zips/.*", ZipHandler),
        (r"/status/.*", StatusHandler),
        (r"/detail/.*", DetailHandler),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
