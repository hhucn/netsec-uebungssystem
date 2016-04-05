from __future__ import unicode_literals

import logging
import os

import tornado.ioloop
import tornado.web

from .webhandler.TableHandler import TableHandler
from .webhandler.SheetsHandler import SheetsHandler
from .webhandler.SheetCreateHandler import SheetCreateHandler
from .webhandler.SheetDeleteHandler import SheetDeleteHandler
from .webhandler.SheetEditEndHandler import SheetEditEndHandler
from .webhandler.SheetRestoreHandler import SheetRestoreHandler
from .webhandler.TaskCreateHandler import TaskCreateHandler
from .webhandler.TaskEditHandler import TaskEditHandler
from .webhandler.TaskDeleteHandler import TaskDeleteHandler
from .webhandler.SheetHandler import SheetHandler
from .webhandler.StudentsHandler import StudentsHandler
from .webhandler.StudentsCreateHandler import StudentsCreateHandler
from .webhandler.StudentHandler import StudentHandler
from .webhandler.SubmissionsHandler import SubmissionsHandler
from .webhandler.SubmissionStudentHandler import SubmissionStudentHandler
from .webhandler.SubmissionStudentSheetHandler import SubmissionStudentSheetHandler
from .webhandler.DownloadHandler import DownloadHandler
from .webhandler.StatusHandler import StatusHandler
from .webhandler.DetailHandler import DetailHandler
from .webhandler.PointsHandler import PointsHandler


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
        (r"/sheet/create", SheetCreateHandler),
        (r"/sheet/([0-9]+)/delete", SheetDeleteHandler),
        (r"/sheet/([0-9]+)/editend", SheetEditEndHandler),
        (r"/sheet/([0-9]+)/restore", SheetRestoreHandler),
        (r"/sheet/([0-9]+)/task/create", TaskCreateHandler),
        (r"/sheet/([0-9]+)/task/([0-9]+)/edit", TaskEditHandler),
        (r"/sheet/([0-9]+)/task/([0-9]+)/delete", TaskDeleteHandler),
        (r"/sheet/.*", SheetHandler),
        (r"/students", StudentsHandler),
        (r"/students/create", StudentsCreateHandler),
        (r"/student/(.*)", StudentHandler),
        (r"/submissions", SubmissionsHandler),
        (r"/submission/([0-9]+)", SubmissionStudentHandler),
        (r"/submission/([0-9]+)/([0-9]+)", SubmissionStudentSheetHandler),
        (r"/download/.*", DownloadHandler),
        (r"/status", StatusHandler),
        (r"/detail/.*", DetailHandler),
        (r"/points", PointsHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(config.module_path, "static")
        }),
    ])

    port = config('httpd.port')
    application.listen(port)
    logging.debug("Web server started on port %i.", port)
    tornado.ioloop.IOLoop.instance().start()
