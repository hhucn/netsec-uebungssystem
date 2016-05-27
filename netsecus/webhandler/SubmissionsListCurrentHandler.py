from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

from .. import submission
from .. import student
from .. import grading
from .. import assignment


class SubmissionsListCurrentHandler(NetsecHandler):
    def get(self):
        current_submission = submission.get_current_full(self.application.db)

        self.render('submissions_list', {'submissions': current_submission, 'heading': "Aktuelle Abgaben"})
