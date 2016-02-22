from __future__ import unicode_literals

import logging
import os
from datetime import datetime

import tornado.ioloop
import tornado.web

from . import helper
from . import database
from .task import Task

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT_PATH, "htmldocs")


class NetsecHandler(helper.RequestHandlerWithAuth):
    def render(self, template, data):
        super(NetsecHandler, self).render(
            os.path.join(TEMPLATE_PATH, "%s.html" % template),
            **data)


class TableHandler(NetsecHandler):
    def get(self):
        sheets = database.getSheets(self.application.config)

        # Count submissions for a sheet
        for sheet in sheets:
            sheetSubmissions = database.getSubmissionForSheet(self.application.config, sheet.id)
            sheet.submissions = len(sheetSubmissions)

            sheetSubmissionsFinished = 0
            for submission in sheetSubmissions:
                if submission.finished:
                    sheetSubmissionsFinished = sheetSubmissionsFinished + 1
            sheet.submissionsFinished = sheetSubmissionsFinished

        self.render("table", {"sheets": sheets})


class DownloadHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri[len("/download/"):]  # cut away "/download/"

        identifier, sha = uri.split("/")
        name = database.getFileName(self.application.config, identifier, sha)

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

        savedstatus = database.getStatus(self.application.config, identifier)

        if not laststatus == savedstatus:
            self.render("status-error", {
                "laststatus": laststatus,
                "currentstatus": currentstatus,
                "identifier": identifier
            })
        else:
            database.setStatus(self.application.config, identifier, currentstatus)
            self.redirect("/detail/%s" % identifier)


class PointsHandler(NetsecHandler):
    def post(self):
        identifier = self.get_argument("identifier")
        sheetNumber = self.get_argument("sheetNumber")
        taskNumber = self.get_argument("taskNumber")
        oldPoints = self.get_argument("oldPoints")
        newPoints = self.get_argument("newPoints")
        reachedPoints = database.getReachedPoints(self.application.config, sheetNumber, taskNumber, identifier)
        maxPoints = 0

        task = database.getTaskFromSheet(self.application.config, sheetNumber, taskNumber)
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
            database.setReachedPoints(self.application.config, sheetNumber, taskNumber, identifier, newPoints)
            self.render("points", {"redirect": 1, "error": "", "oldPoints": oldPoints, "reachedPoints": newPoints,
                        "taskNumber": taskNumber, "sheetNumber": sheetNumber, "identifier": identifier})


class SheetManagerHandler(NetsecHandler):
    def post(self):
        manageType = self.get_argument("type")

        if manageType == "renameSheet":
            oldName = self.get_argument("oldName")
            newName = self.get_argument("newName")
            sheetID = self.get_argument("sheetID")

            sheet = database.getSheetFromID(self.application.config, sheetID)

            if not sheet:
                self.render("sheet-error", {"error": "idNotFound"})
                return

            if not str(sheet.name) == oldName:
                self.render("sheet-error", {"error": "modified"})
                return

            if database.getSheetFromNumber(self.application.config, newName):
                self.render("sheet-error", {"error": "exists"})
                return

            database.setSheetNameForID(self.application.config, sheetID, oldName, newName)
            self.redirect("/sheet/%s" % sheetID)
        elif manageType == "addSheet":
            database.setSheet(self.application.config, self.get_argument("name"))
            self.redirect("/sheets")
        elif manageType == "editTask":
            sheetID = self.get_argument("sheetID")
            taskID = self.get_argument("taskID")
            oldName = self.get_argument("oldName")
            newName = self.get_argument("newName")
            oldDesc = self.get_argument("oldDescription")
            newDesc = self.get_argument("newDescription")
            oldPoints = float(self.get_argument("oldPoints"))
            newPoints = float(self.get_argument("newPoints"))

            currentTask = database.getTaskFromID(self.application.config, taskID)

            if(oldName == currentTask.name and oldDesc == currentTask.description and
               oldPoints == currentTask.maxPoints):
                newTask = Task(taskID, sheetID, newName, newDesc, newPoints)
                database.replaceTask(self.application.config, taskID, newTask)
                self.redirect("/sheet/%s" % sheetID)
            else:
                self.render("task-error", {"error": "modified"})
        elif manageType == "newTask":
            sheetID = self.get_argument("sheetID")
            taskName = self.get_argument("name")
            taskDescription = self.get_argument("description")
            taskPoints = self.get_argument("points")
            database.setNewTaskForSheet(self.application.config, sheetID, taskName, taskDescription, taskPoints)
            self.redirect("/sheet/%s" % sheetID)
        else:
            logging.error("Specified SheetManager type '%s' does not exist." % manageType)


class TaskDeleteHandler(NetsecHandler):
    def post(self, sheet_id, task_id):
        database.deleteTask(self.application.config, int(task_id))
        self.redirect("/sheet/%s" % sheet_id)


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
                                   'korrekturstatus': database.getStatus(self.application.config, identifier),
                                   'sheets': database.getSheets(self.application.config, identifier)})
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)
            self.redirect("/")


class SheetsHandler(NetsecHandler):
    def get(self):
        sheets = database.getSheets(self.application.config)
        self.render('sheets', {'sheets': sheets})


class SheetHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        requestedSheet = uri[2:][0]  # remove empty element and "sheet", get sheet number

        sheet = database.getSheetFromID(self.application.config, requestedSheet)

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
        (r"/sheet/([0-9]+)/task/([0-9]+)/delete", TaskDeleteHandler),
        (r"/sheet/.*", SheetHandler),
        (r"/sheetmanager", SheetManagerHandler),
        (r"/download/.*", DownloadHandler),
        (r"/status", StatusHandler),
        (r"/detail/.*", DetailHandler),
        (r"/points", PointsHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(ROOT_PATH, "static")
        }),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
