from __future__ import unicode_literals

import os.path

import tornado.web

from .. import file
from .. import submission


class DownloadHandler(tornado.web.StaticFileHandler):
    def initialize(self):
        super(DownloadHandler, self).initialize(self.application.config.module_path)

    def get(self, hash):
        requested_file = file.get_from_hash(self.application.db, hash)
        file_submission = submission.get_from_id(self.application.db, requested_file.submission_id)
        requested_file_relpath = os.path.join(file_submission.files_path, requested_file.filename)
        requested_file_abspath = os.path.join(self.application.config.module_path, requested_file_relpath)

        super(tornado.web.StaticFileHandler, self).get(requested_file_abspath)
