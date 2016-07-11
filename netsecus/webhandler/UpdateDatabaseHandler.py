from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler
from .. import helper

import sqlite3


class UpdateDatabaseHandler(NetsecHandler):
    def get(self):
        db = self.application.db

        # Add deleted field to student and submission table (for merged)
        try:
            db.cursor.execute(
                '''ALTER TABLE student ADD deleted INTEGER(1)''')
        except sqlite3.OperationalError:
            pass  # Column name exists already
        try:
            db.cursor.execute(
                '''ALTER TABLE submission ADD deleted INTEGER(1)''')
        except sqlite3.OperationalError:
            pass  # Column name exists already
        db.commit()

        # Add emails to alias table
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
