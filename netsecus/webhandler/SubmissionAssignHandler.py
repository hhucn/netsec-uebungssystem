from __future__ import unicode_literals

from .ProtectedPostHandler import ProtectedPostHandler

from .. import assignment
from .. import submission


class SubmissionAssignHandler(ProtectedPostHandler):
    def postPassedCSRF(self, submission_id):
        subm = submission.get_from_id(self.application.db, submission_id)
        grader = self.get_argument("grader")

        assignment.set_for_student_and_sheet(self.application.db,
                                             subm.student_id,
                                             subm.sheet_id,
                                             grader)

        self.redirect("/submission/%s" % submission_id)
