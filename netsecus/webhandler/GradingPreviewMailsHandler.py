from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import grading


class GradingPreviewMailsHandler(NetsecHandler):
    def get(self):
        grading_results = grading.unsent_results(self.application.db)
        grading.enrich_results(self.application.db, grading_results)

        self.render('grading_send', {
            'grading_results': grading_results,
        })
