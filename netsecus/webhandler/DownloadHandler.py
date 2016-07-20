from __future__ import unicode_literals

import mimetypes

from ..helper import RequestHandlerWithAuth

from .. import file


class DownloadHandler(RequestHandlerWithAuth):
    def get(self, hash):
        requested_file = file.get_from_hash(self.application.db, hash)
        requested_file_type, encoding = mimetypes.guess_type(requested_file.filename)

        if not requested_file_type:
            requested_file_type = "application/octet-stream"

        self.set_header("Content-Type", requested_file_type)
        self.set_header("Content-Disposition", "attachment; filename=%s" % requested_file.filename)

        self.write(file.get_content_for_hash(self.application.db, self.config, hash))
