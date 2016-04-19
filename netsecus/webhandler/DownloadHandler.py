from __future__ import unicode_literals

import os.path

from ..helper import RequestHandlerWithAuth

from .. import file
from .. import submission


class DownloadHandler(RequestHandlerWithAuth):
    def get(self, hash):
        requested_file = file.get_from_hash(self.application.db, hash)
        file_submission = submission.get_from_id(self.application.db, requested_file.submission_id)
        requested_file_relpath = os.path.join(file_submission.files_path, requested_file.filename)
        requested_file_abspath = os.path.join(self.application.config.module_path, requested_file_relpath)

        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=%s" % requested_file.filename)
        with open(requested_file_abspath, "rb") as requested_file_handle:
            content = requested_file_handle.read()
            self.write(content)
