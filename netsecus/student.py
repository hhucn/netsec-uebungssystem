from __future__ import unicode_literals

import collections

Student = collections.namedtuple('Student', ['id'])

# TODO do name resolution etc. here
def resolve_by_email(config, database, message):
    user_id = message.get('From', 'anonymous')
    database = Database(config)
    alias = database.resolveAlias(user_id)
    return alias
