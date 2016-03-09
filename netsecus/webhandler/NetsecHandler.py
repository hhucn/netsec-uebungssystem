from __future__ import unicode_literals

import os

from .. import helper

class NetsecHandler(helper.RequestHandlerWithAuth):
    def render(self, template, data):
        super(NetsecHandler, self).render(
            os.path.join(TEMPLATE_PATH, "%s.html" % template),
            **data)
