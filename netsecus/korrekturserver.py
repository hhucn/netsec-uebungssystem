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
                        "status": korrekturtools.getStatus(self.application.config, entry.lower()),
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


class DownloadHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri[len("/download/"):]  # cut away "/download/"

        identifier, sha = uri.split("/")
        name = korrekturtools.getFileName(self.application.config, identifier, sha)

        attachmentPath = self.application.config("attachment_path")
        filePath = os.path.join(attachmentPath, identifier, "%s %s" % (sha, name))

        self.set_header("Content-Type", "application/x-octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=" + name)

        with open(filePath, "r") as f:
            self.write(f.read())

        self.finish()


class StatusHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        laststatus = self.get_argument("laststatus")
        currentstatus = self.get_argument("currentstatus")

        savedstatus = korrekturtools.getStatus(self.application.config, identifier)

        if not laststatus == savedstatus:
            self.render("status", {"redirect": 0, "laststatus": laststatus,
                        "currentstatus": currentstatus, "identifier": identifier})
        else:
            korrekturtools.setStatus(self.application.config, identifier, currentstatus)
            self.render("status", {"redirect": 1, "currentstatus": currentstatus, "identifier": identifier})


class PointsHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        sheetNumber = self.get_argument("sheetNumber")
        taskNumber = self.get_argument("taskNumber")
        oldPoints = self.get_argument("oldPoints")
        newPoints = self.get_argument("newPoints")
        reachedPoints = korrekturtools.getReachedPoints(self.application.config, sheetNumber, taskNumber, identifier)

        if not oldPoints == str(reachedPoints):
            self.render("points", {"redirect": 0, "oldPoints": oldPoints, "reachedPoints": reachedPoints,
                        "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})
        else:
            korrekturtools.setReachedPoints(self.application.config, sheetNumber, taskNumber, identifier, newPoints)
            self.render("points", {"redirect": 1, "oldPoints": oldPoints, "reachedPoints": newPoints,
                        "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})


class DetailHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        identifier = uri[2:][0]  # remove empty element and "detail", get student ID

        files = []

        attachmentPath = self.application.config("attachment_path")
        if os.path.exists(attachmentPath):
            studentAttachmentPath = os.path.join(attachmentPath, helper.escapePath(identifier))
            for entry in os.listdir(studentAttachmentPath):
                if entry[0] != ".":
                    pathToFile = os.path.join(studentAttachmentPath, entry)
                    fileHash, name = entry.split(" ", 1)
                    filesize = os.path.getsize(pathToFile) / 1024
                    fileDateTimestamp = os.path.getmtime(pathToFile)
                    fileDateTime = datetime.fromtimestamp(fileDateTimestamp).strftime("%Y-%m-%d %H:%M:%S %z")

                    if filesize == 0:
                        filesize = 1

                    files.append({
                        "name": name,
                        "size": "%i KB" % filesize,
                        "date": fileDateTime,
                        "hash": fileHash
                        })
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)

        self.render('detail', {'identifier': identifier, 'files': files,
                               'korrekturstatus': korrekturtools.getStatus(self.application.config, identifier),
                               'sheets': korrekturtools.getSheets(self.application.config, identifier)})


class TaskHandler(NetsecHandler):
    def get(self):
        sheets = korrekturtools.getSheets(self.application.config)
        self.render('task', {'sheets': sheets})


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
        (r"/tasks", TaskHandler),
        (r"/zips/.*", ZipHandler),
        (r"/download/.*", DownloadHandler),
        (r"/status", StatusHandler),
        (r"/detail/.*", DetailHandler),
        (r"/points", PointsHandler),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
