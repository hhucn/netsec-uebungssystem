from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import assignment
from .. import grading
from .. import student
from .. import submission


class OverviewHandler(NetsecHandler):
    def get(self):
        grader = self.request.netsecus_user
        submissions = []
        
        for sub in submission.get_all_full(self.application.db):
            if sub["grader"] == grader:
                submissions.append(sub)


        self.render('submissions_list', {'submissions': submissions, 'heading': "Abgaben für %s" % grader})
