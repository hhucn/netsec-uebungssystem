from __future__ import unicode_literals

import re

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
    return '%s' % student.id
