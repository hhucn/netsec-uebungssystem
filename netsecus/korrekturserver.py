from __future__ import unicode_literals

import logging
import os
from datetime import datetime
import io

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
                        "status": korrekturtools.readStatus(self.application.config, entry.lower()),
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
    def post(self):
        identifier = self.get_argument("identifier")
        laststatus = self.get_argument("laststatus")
        currentstatus = self.get_argument("currentstatus")

        savedstatus = korrekturtools.readStatus(self.application.config, identifier)

        if not laststatus == savedstatus:
            self.render("status", { "redirect": 0, "laststatus": laststatus, "currentstatus": currentstatus, "identifier": identifier })
        else:
            korrekturtools.writeStatus(self.application.config, identifier, currentstatus)
            self.render("status", { "redirect": 1, "currentstatus": currentstatus, "identifier": identifier })



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
                    with io.open(os.path.join(studentAttachmentPath, "mailtext.txt"), "rt") as mailfile:
                        mailtext = mailfile.read()
                    if not mailtext:
                        mailtext = "Kein Text mitgesendet."
                elif entry[0] != ".":
                    timestamp, name = entry.split(" ", 1)
                    files.append({
                        "name": name,
                        "size": "%s KB" % str(os.path.getsize(os.path.join(studentAttachmentPath, entry)) / 1024),
                        "date": datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d %H-%M")
                        })
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        self.render('detail', {'identifier': uri, 'files': files, 'mailtext': mailtext, 'korrekturstatus': korrekturtools.readStatus(self.application.config, uri)})


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
        (r"/status?.*", StatusHandler),
        (r"/detail/.*", DetailHandler),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
