from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler


class ProtectedPostHandler(NetsecHandler):
    def post(self, *args):
        self.check_xsrf_cookie()
        self.postPassedCSRF(*args)
