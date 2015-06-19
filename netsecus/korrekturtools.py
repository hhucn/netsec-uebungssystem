from __future__ import unicode_literals

import sqlite3

from .sheet import Sheet
from .task import Task


# Getter methods for values from tables

def getStatus(config, student):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
    cursor.execute("SELECT status FROM status WHERE identifier = ?", (student,))
    statusRow = cursor.fetchone()

    if statusRow:
        return statusRow[0]  # get first column, "status"
    else:
        return "Unbearbeitet"


def getFileName(config, identifier, sha):
    fileDatabase = getFileTable(config)
    cursor = fileDatabase.cursor()

    cursor.execute("SELECT name FROM files WHERE identifier = ? AND sha = ?", (identifier, sha,))
    return cursor.fetchone()[0]


def getReachedPoints(config, sheetNumber, taskNumber, identifier):
    pointsDatabase = getPointsTable(config)
    cursor = pointsDatabase.cursor()

    cursor.execute("SELECT reachedPoints FROM points WHERE sheetNumber = ? AND taskNumber = ? AND identifier = ?",
                   (sheetNumber, taskNumber, identifier,))

    reachedPoints = cursor.fetchone()

    if reachedPoints:
        return reachedPoints

    return 0


def getTasksForSheet(config, sheetNumber, student=None):
    taskDatabase = getTaskTable(config)
    cursor = taskDatabase.cursor()

    cursor.execute("SELECT taskNumber, description, maxPoints FROM tasks WHERE sheetNumber = ?", (sheetNumber, ))
    tasks = cursor.fetchall()

    taskObjects = []

    for task in tasks:
        taskNumber, description, maxPoints = task
        reachedPoints = 0

        if student:
            reachedPoints = getReachedPoints(config, sheetNumber, taskNumber, student)

        taskObjects.append(Task(taskNumber, description, maxPoints, reachedPoints))

    return taskObjects


def getSheets(config, student=None):
    sheetDatabase = getSheetTable(config)
    sheetCursor = sheetDatabase.cursor()

    sheetCursor.execute("SELECT number FROM sheets")

    sheetObjects = []

    for sheet in sheetCursor.fetchall():
        sheetNumber = sheet[0]
        tasksForSheet = getTasksForSheet(config, sheetNumber, student)
        sheetObjects.append(Sheet(sheetNumber, tasksForSheet))

    return sheetObjects


# Setter methods for table values

def setStatus(config, student, status):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
    cursor.execute("SELECT status FROM status WHERE identifier = ?", (student,))
    statusRow = cursor.fetchone()

    if statusRow:
        cursor.execute("UPDATE status SET status = ? WHERE identifier = ?", (status, student,))
    else:
        cursor.execute("INSERT INTO status VALUES(?, ?)", (student, status, ))
    database.commit()


def setFile(config, identifier, sha, name):
    fileDatabase = getFileTable(config)
    cursor = fileDatabase.cursor()

    cursor.execute("SELECT name FROM files WHERE identifier = ? AND sha = ?", (identifier, sha,))

    if not cursor.fetchone():
        # doesn't exist, create now.
        # if this is true (already exists), there's no need to create
        # it again, as it is the same file. Some user uploaded a file
        # with the same content and the same name twice.
        cursor.execute("INSERT INTO files VALUES(?, ?, ?)", (identifier, sha, name,))
        fileDatabase.commit()


# Table getter methods

def getFileTable(config):
    fileDatabasePath = config("database_path")
    fileDatabase = sqlite3.connect(fileDatabasePath)
    cursor = fileDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS files
        (`identifier` text, `sha` text, `name` text);""")
    return fileDatabase


def getStatusTable(config):
    statusDatabasePath = config("database_path")
    statusDatabase = sqlite3.connect(statusDatabasePath)
    cursor = statusDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS status
         (`identifier` text UNIQUE, `status` text, PRIMARY KEY (`identifier`));""")
    return statusDatabase


def getPointsTable(config):
    pointsDatabasePath = config("database_path")
    pointsDatabase = sqlite3.connect(pointsDatabasePath)
    cursor = pointsDatabase.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS points
         (`sheetNumber` int, `taskNumber` int, `identifier` text, `reachedPoints` float);""")
    return pointsDatabase


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
