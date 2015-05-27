from __future__ import unicode_literals

import os
import logging
import sqlite3

from . import helper


def readStatus(config, student):
    database = getStatusTable(config)
    cursor = database.cursor()

    cursor.execute("SELECT status FROM status WHERE identifier = ?", (student,))
    statusRow = cursor.fetchone()[0]  # just get first status

    if statusRow:
        return statusRow
    else:
        return "Unbearbeitet"


def writeStatus(config, student, status):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
    cursor.execute("SELECT status FROM status WHERE identifier = ?", (student,))
    statusRow = cursor.fetchone()[0]

    if statusRow:
        cursor.execute("UPDATE status SET status = ? WHERE identifier = ?", (status, student,))
    else:
        cursor.execute("INSERT INTO status VALUES(?, ?)", (student, status, ))
    database.commit()


def getStatusTable(config):
    statusDatabasePath = config("database_path")
    statusDatabase = sqlite3.connect(statusDatabasePath)
    cursor = statusDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS status
         (`identifier` text UNIQUE, `status` text, PRIMARY KEY (`identifier`));""")
    return statusDatabase
