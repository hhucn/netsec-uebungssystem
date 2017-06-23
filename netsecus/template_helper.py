from __future__ import unicode_literals

import datetime
import re

import tornado.template

from . import helper


def alias2name(alias):
    # TODO aliases should really be already encoded. For now, encode it twice
    a_decoded = helper.decode_mail_words(alias)

    m = re.match(r'^(.*?)\s*<.*@.*>$', a_decoded)
    username = m.group(1) if m else a_decoded

    return username


def format_student(student):
    usernames = helper.remove_duplicates(alias2name(a) for a in student.aliases)
    if usernames:
        return '/'.join(usernames)
    return 'Student %s' % student.student.id


def format_points(decipoints):
    if decipoints is None:
        return ''

    points = (decipoints / 10.)

    if points == int(points):
        points = int(points)

    return '%s' % points


def format_timestamp(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M:%S')


def format_percent(quotient):
    return "%i%%" % int(quotient * 100)


def translate_status(status):
    return {
        "started": "Angefangen",
        "done": "Fertig",
        "assigned": "Zugewiesen",
    }.get(status, "Unbearbeitet")


# Render from outside a tornado handler
def render_template(template_body, variables):
    tmpl = tornado.template.Template(template_body)
    html = tmpl.generate(**variables)
    return html
