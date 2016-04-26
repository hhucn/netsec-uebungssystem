from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import grading


class OverviewHandler(NetsecHandler):
    def get(self):
        grader = self.request.netsecus_user
        sheets = grading.get_grades_for_grader(self.application.db, grader)
        self.render('overview', {'sheets': sheets, 'grader': grader})
