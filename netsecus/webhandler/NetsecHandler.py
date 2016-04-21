from __future__ import unicode_literals

import os

from .. import helper
from .. import template_helper


class NetsecHandler(helper.RequestHandlerWithAuth):
    def render(self, template, data):
        TEMPLATE_PATH = os.path.join(self.application.config.module_path, "templates")
        data['template_helper'] = template_helper

        super(NetsecHandler, self).render(
            os.path.join(TEMPLATE_PATH, "%s.html" % template),
            **data)
