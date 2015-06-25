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
            self.render("status-error", {
                "laststatus": laststatus,
                "currentstatus": currentstatus,
                "identifier": identifier
            })
        else:
            korrekturtools.setStatus(self.application.config, identifier, currentstatus)
            self.redirect("/detail/%s" % identifier)


class PointsHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        sheetNumber = self.get_argument("sheetNumber")
        taskNumber = self.get_argument("taskNumber")
        oldPoints = self.get_argument("oldPoints")
        newPoints = self.get_argument("newPoints")
        reachedPoints = korrekturtools.getReachedPoints(self.application.config, sheetNumber, taskNumber, identifier)
        maxPoints = 0

        task = korrekturtools.getTaskFromSheet(self.application.config, sheetNumber, taskNumber)
        if task:
            maxPoints = task.maxPoints

        if not float(oldPoints) == reachedPoints:
            # Someone submitted new points after this user opened the detail page, but before he could submit his points
            self.render("points", {"redirect": 0, "error": "modified", "oldPoints": oldPoints,
                                   "reachedPoints": reachedPoints, "taskNumber": taskNumber, "sheetNumber": sheetNumber,
                                   "identifier": identifier})
        elif maxPoints < float(newPoints):
            self.render("points", {"redirect": 0, "error": "overMaxPoints", "oldPoints": oldPoints,
                                   "reachedPoints": reachedPoints, "taskNumber": taskNumber, "sheetNumber": sheetNumber,
                                   "identifier": identifier})
        else:
            korrekturtools.setReachedPoints(self.application.config, sheetNumber, taskNumber, identifier, newPoints)
            self.render("points", {"redirect": 1, "error": "", "oldPoints": oldPoints, "reachedPoints": newPoints,
                        "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})


class SheetManagerHandler(NetsecHandler):
    def post(self):
        manageType = self.get_argument("type")

        if manageType == "renameSheet":
            oldNumber = self.get_argument("oldNumber")
            newNumber = self.get_argument("newNumber")
            sheetID = self.get_argument("sheetID")

            sheet = korrekturtools.getSheetFromID(self.application.config, sheetID)

            if not sheet:
                self.render("sheet-error", {"error": "idNotFound"})
                return

            if not str(sheet.number) == oldNumber:
                self.render("sheet-error", {"error": "modified"})
                return

            if korrekturtools.getSheetFromNumber(self.application.config, newNumber):
                self.render("sheet-error", {"error": "exists"})
                return

            korrekturtools.setSheetNumberForID(self.application.config, sheetID, oldNumber, newNumber)
            self.redirect("/sheet/%s" % newNumber)
        elif manageType == "editTask":
            print("a")
        elif manageType == "newTask":
            print("a")
        else:
            logging.error("Specified SheetManager type '%s' does not exist." % manageType)


class DetailHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        identifier = uri[2:][0]  # remove empty element and "detail", get student ID

        files = []

        attachmentPath = os.path.join(self.application.config("attachment_path"), helper.escapePath(identifier))
        if os.path.exists(attachmentPath):
            for entry in os.listdir(attachmentPath):
                if entry[0] != ".":
                    pathToFile = os.path.join(attachmentPath, entry)
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
            self.render('detail', {'identifier': identifier, 'files': files,
                                   'korrekturstatus': korrekturtools.getStatus(self.application.config, identifier),
                                   'sheets': korrekturtools.getSheets(self.application.config, identifier)})
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)
            self.redirect("/")


class SheetsHandler(NetsecHandler):
    def get(self):
        sheets = korrekturtools.getSheets(self.application.config)
        self.render('sheets', {'sheets': sheets})


class SheetHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        requestedSheet = uri[2:][0]  # remove empty element and "sheet", get sheet number

        sheet = korrekturtools.getSheetFromNumber(self.application.config, requestedSheet)

        if sheet:
            self.render('sheet', {'sheet': sheet})
        else:
            logging.error("Specified sheet ('%s') does not exist." % requestedSheet)
            self.redirect("/sheets")


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
        (r"/sheets", SheetsHandler),
        (r"/sheet/.*", SheetHandler),
        (r"/sheetmanager", SheetManagerHandler),
        (r"/download/.*", DownloadHandler),
        (r"/status", StatusHandler),
        (r"/detail/.*", DetailHandler),
        (r"/points", PointsHandler),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
