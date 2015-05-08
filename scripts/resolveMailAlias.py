from __future__ import unicode_literals

import sqlite3


def run(config, imapmail, mails, *args):
    aliasDatabasePath = config("database_path")
    aliasDatabase = sqlite3.connect(aliasDatabasePath)
    cursor = aliasDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS aliases
         (`alias` text UNIQUE, `destination` text UNIQUE, PRIMARY KEY (`alias`));""")

    for mail in mails:
        mail.address["identifier"] = getDestinationForAlias(mail.address["identifier"], cursor)

    return mails


def getDestinationForAlias(alias, cursor):
    cursor.execute("SELECT destination FROM aliases WHERE alias = ?", (alias,))
    destination = cursor.fetchone()
    if not destination:
        return alias
    else:
        return getDestinationForAlias(destination[0], cursor)
