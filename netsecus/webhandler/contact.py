from __future__ import unicode_literals

from .. import grading
from .. import sendmail
from .. import sheet
from .. import student

from .NetsecHandler import NetsecHandler
from .ProtectedPostHandler import ProtectedPostHandler


def calc_data(db, student_id):
    fs = student.get_full_student(db, student_id)
    all_sheet_points = sheet.get_all_total_score(db)
    student_track = grading.get_student_track(db, all_sheet_points, student_id)
    total_decipoints = sum(st.get('decipoints', 0) for st in student_track)
    total_max_decipoints = sum(st['max_decipoints'] for st in student_track)

    return {
        'fs': fs,
        'student_track': student_track,
        'total_decipoints': total_decipoints,
        'total_max_decipoints': total_max_decipoints,
    }


class ContactCraftHandler(NetsecHandler):
    def get(self, student_id_str):
        data = calc_data(self.db, int(student_id_str))
        self.render('contact_craft', data)


class ContactSendHandler(ProtectedPostHandler):
    def postPassedCSRF(self, student_id_str):
        data = calc_data(self.db, int(student_id_str))
        data['message'] = self.get_argument('message')

        to = data['fs'].primary_alias
        subject = 'Netzwerksicherheit: Punktestand'
        body = self.render2string('contact_mail', data)

        with sendmail.Mailer(self.application.config) as mailer:
            mailer.send(to, subject, body)

        self.redirect('/student/%d?sent' % data['fs'].student.id)
