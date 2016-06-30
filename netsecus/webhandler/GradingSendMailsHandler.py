from __future__ import unicode_literals

from .. import grading
from .. import sendmail
from .. import sheet


from .ProtectedPostHandler import ProtectedPostHandler


class GradingSendMailsHandler(ProtectedPostHandler):
    def postPassedCSRF(self):
        db = self.application.db

        grading_results = grading.unsent_results(db)
        grading.enrich_results(db, grading_results)

        # Assemble student tracks
        all_sheet_points = sheet.get_all_total_score(db)
        total_max_decipoints = sum(asp['decipoints'] for asp in all_sheet_points)
        for gr in grading_results:
            gr['student_track'] = grading.get_student_track(db, all_sheet_points, gr['student_id'])
            gr['total_decipoints'] = sum(st.get('decipoints', 0) for st in gr['student_track'])
            gr['total_max_decipoints'] = total_max_decipoints

        with sendmail.Mailer(self.application.config) as mailer:
            for gr in grading_results:
                body = self.render2string('mail_grading', gr)
                subject = 'Korrektur Abgabe %s' % gr['sheet_id']
                to = gr['named_student'].aliases[0]
                mailer.send(to, subject, body)

                # TODO upload on imap
                mail_uid = -1

                grading.on_send_result(db, gr['id'], mail_uid)

        self.redirect('/grading/mails/preview')
