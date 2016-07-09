from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import helper


# Adds emails to the alias table
class FixAddEmailHandler(NetsecHandler):
    def get(self):
        db = self.application.db
        import sqlite3
        try:
            db.cursor.execute(
                '''ALTER TABLE alias ADD email TEXT''')
        except sqlite3.OperationalError:
            pass  # Column name exists already

        db.cursor.execute(
                '''SELECT id, alias FROM alias''')
        arows = db.cursor.fetchall()

        for arow in arows:
            aid, alias = arow
            email = helper.alias2mail(alias)
            assert email
            db.cursor.execute(
                '''UPDATE alias SET email=? WHERE id=?''', (email, aid))
            assert db.cursor.rowcount == 1
        db.commit()
