from __future__ import unicode_literals

from .. import grading
from .. import sendmail

from .ProtectedPostHandler import ProtectedPostHandler


class GradingSendMailsHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        grading_results = grading.unsent_results(self.application.db)
        grading.enrich_results(self.application.db, grading_results)

        with sendmail.Mailer(self.application.config) as mailer:
            for gr in grading_results:
                body = self.render2string('mail_grading', gr)
                subject = 'Korrektur Abgabe %s' % gr['sheet_id']
                to = gr['named_student'].aliases[0]
                mailer.send(to, subject, body)

                # TODO upload on imap
                mail_uid = -1

                grading.on_send_result(self.application.db, gr['id'], mail_uid)

        self.redirect('/grading/mails/preview')
