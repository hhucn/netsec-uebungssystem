from __future__ import unicode_literals

from .. import grading
from .. import sheet
from .. import student
from .NetsecHandler import NetsecHandler


class StudentHandler(NetsecHandler):
    def get(self, student_id):
        fs = student.get_full_student(self.application.db, student_id)

        grading_results = grading.all_results(
            self.application.db,
            'status=? AND student_id=?', ('done', student_id,))
        max_decipoints = sheet.get_all_total_score_by_sheet(self.application.db)
        for gr in grading_results:
            gr['total_decipoints'] = max_decipoints[gr['sheet_id']]

        submission_with_score = []
        student_total_score = 0
        added_sheets = set()
        
        for subm in fs.submissions:
            student_score = 0

            for gr in grading_results:
                if gr["sheet_id"] == subm.sheet_id:
                    student_score = gr["decipoints"]
                    if student_score is None:
                        print('gr: %r' % gr)
                    total_score = gr["total_decipoints"]
                    submission_with_score.append({
                        "submission": subm,
                        "student_score": student_score,
                        "total_score": total_score,
                    })
                    
                    if subm.sheet_id not in added_sheets:
                        student_total_score += student_score
                        added_sheets.add(subm.sheet_id)
                    break

        self.render('student', {
            'student': fs.student,
            'aliases': fs.aliases,
            'submissions': submission_with_score,
            'student_total_score': student_total_score,
            'reachable_total_score': sheet.get_all_total_score_number(self.application.db),
        })
