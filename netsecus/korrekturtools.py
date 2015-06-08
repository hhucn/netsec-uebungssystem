from __future__ import unicode_literals

import sqlite3

from .sheet import Sheet
from .task import Task


def readStatus(config, student):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
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


def getTasksForSheet(config, sheetNumber):
    taskDatabasePath = config("database_path")
    taskDatabase = sqlite3.connect(taskDatabasePath)
    cursor = taskDatabase.cursor()

    cursor.execute("SELECT taskNumber, description, maxPoints FROM tasks WHERE sheetNumber = ?", (sheetNumber, ))
    tasks = cursor.fetchall()

    taskObjects = []

    for task in tasks:
        # 0: taskNumber, 1: description, 2: maxPoints
        taskObjects.append(Task(task[0], task[1], task[2]))

    return taskObjects


def getSheets(config):
    sheetDatabase = getSheetTable(config)
    sheetCursor = sheetDatabase.cursor()
    taskDatabase = getTaskTable(config)
    sheetCursor = taskDatabase.cursor()

    sheetCursor.execute("SELECT number FROM sheets")

    sheetObjects = []

    for sheet in sheetCursor.fetchall():
        # 'number' value is in column #0
        tasksForSheet = getTasksForSheet(config, sheet[0])
        sheetObjects.append(Sheet(sheet[0], tasksForSheet))

    return sheetObjects


def getStatusTable(config):
    statusDatabasePath = config("database_path")
    statusDatabase = sqlite3.connect(statusDatabasePath)
    cursor = statusDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS status
         (`identifier` text UNIQUE, `status` text, PRIMARY KEY (`identifier`));""")
    return statusDatabase


def getSheetTable(config):
    sheetDatabasePath = config("database_path")
    sheetDatabase = sqlite3.connect(sheetDatabasePath)
    cursor = sheetDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sheets
         (`number` int UNIQUE, PRIMARY KEY (`number`));""")
    return sheetDatabase


def getTaskTable(config):
    taskDatabasePath = config("database_path")
    taskDatabase = sqlite3.connect(taskDatabasePath)
    cursor = taskDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (`id` int AUTO_INCREMENT, `sheetNumber` int,
        `taskNumber` int, `description` text, `maxPoints` float, PRIMARY KEY (`id`));""")
    return taskDatabase
