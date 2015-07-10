from __future__ import unicode_literals

import sqlite3

from .sheet import Sheet
from .task import Task


# Getter methods for values from tables

def getStatus(config, identifier, sheetID):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
    cursor.execute("SELECT status FROM status WHERE identifier = ? AND sheetID = ?", (identifier, sheetID))
    statusRow = cursor.fetchone()

    if statusRow:
        return statusRow[0]  # get first column, "status"
    else:
        return "Unbearbeitet"


def getFileName(config, identifier, sha, sheetID):
    fileDatabase = getFileTable(config)
    cursor = fileDatabase.cursor()

    cursor.execute("SELECT name FROM files WHERE identifier = ? AND sha = ? AND sheetID = ?",
                   (identifier, sha, sheetID))
    return cursor.fetchone()[0]


def getReachedPoints(config, sheetID, taskID, identifier):
    pointsDatabase = getPointsTable(config)
    cursor = pointsDatabase.cursor()

    cursor.execute("SELECT reachedPoints FROM points WHERE sheetID = ? AND taskID = ? AND identifier = ?",
                   (sheetID, taskID, identifier,))

    reachedPoints = cursor.fetchone()

    if reachedPoints:
        return reachedPoints[0]

    return 0


def getTaskFromSheet(config, sheetID, taskID):
    taskDatabase = getTaskTable(config)
    cursor = taskDatabase.cursor()

    cursor.execute("SELECT name, description, maxPoints FROM tasks WHERE sheetID = ? AND taskID = ?", (sheetID, taskID))
    task = cursor.fetchone()

    if task:
        name, description, maxPoints = task
        return Task(taskID, name, description, maxPoints, 0)

    return None


def getTasksForSheet(config, sheetID, student=None):
    taskDatabase = getTaskTable(config)
    cursor = taskDatabase.cursor()

    cursor.execute("SELECT taskID, name, description, maxPoints FROM tasks WHERE sheetID = ?", (sheetID, ))
    tasks = cursor.fetchall()

    taskObjects = []

    for task in tasks:
        taskNumber, taskName, description, maxPoints = task
        reachedPoints = 0

        if student:
            reachedPoints = getReachedPoints(config, sheetID, taskNumber, student)

        taskObjects.append(Task(taskNumber, taskName, description, maxPoints, reachedPoints))

    return taskObjects


def getSheetFromNumber(config, sheetName):
    sheetDatabase = getSheetTable(config)
    cursor = sheetDatabase.cursor()

    cursor.execute("SELECT sheetID, editable, start, end FROM sheets WHERE name = ?", (sheetName, ))
    sheet = cursor.fetchone()

    if sheet:
        tasks = getTasksForSheet(config, sheetName)
        rowID, editable, start, end = sheet
        editable = editable == "1"

        return Sheet(rowID, sheetName, tasks, editable, start, end)
    return None


def getSheetFromID(config, sheetID):
    sheetDatabase = getSheetTable(config)
    cursor = sheetDatabase.cursor()

    cursor.execute("SELECT name, editable FROM sheets WHERE sheetID = ?", (sheetID, ))
    sheet = cursor.fetchone()

    if sheet:
        sheetName = sheet[0]
        editable = (sheet[1] == "1")
        tasks = getTasksForSheet(config, sheetID)

        return Sheet(sheetID, sheetName, tasks, editable)
    return None


def getSheets(config, student=None):
    sheetDatabase = getSheetTable(config)
    sheetCursor = sheetDatabase.cursor()

    sheetCursor.execute("SELECT sheetID, name, editable FROM sheets")

    sheetObjects = []

    for sheet in sheetCursor.fetchall():
        sheetID = sheet[0]
        name = sheet[1]
        editable = (sheet[2] == "1")  # SQLite doesn't support boolean, so we use 0/1
        tasksForSheet = getTasksForSheet(config, sheetID, student)
        sheetObjects.append(Sheet(sheetID, name, tasksForSheet, editable))

    return sheetObjects


# Setter methods for table values

def setStatus(config, student, sheetID, status):
    database = getStatusTable(config)
    cursor = database.cursor()

    # Check if we need to create a new row first
    cursor.execute("SELECT status FROM status WHERE identifier = ? AND sheetID = ?", (student, sheetID))
    statusRow = cursor.fetchone()

    if statusRow:
        cursor.execute("UPDATE status SET status = ? WHERE identifier = ? AND sheetID = ?", (status, student, sheetID))
    else:
        cursor.execute("INSERT INTO status VALUES(?, ?, ?)", (student, sheetID, status))
    database.commit()


def setSheet(config, name):
    database = getStatusTable(config)
    cursor = database.cursor()

    cursor.execute("INSERT INTO sheets (name) VALUES(?)", (name, ))
    database.commit()


def setFile(config, identifier, sheetID, sha, name):
    fileDatabase = getFileTable(config)
    cursor = fileDatabase.cursor()

    cursor.execute("SELECT name FROM files WHERE identifier = ? AND sha = ? AND sheetID = ?",
                   (identifier, sha, sheetID))

    if not cursor.fetchone():
        # doesn't exist, create now.
        # if this is true (already exists), there's no need to create
        # it again, as it is the same file. Some user uploaded a file
        # with the same content and the same name twice.
        cursor.execute("INSERT INTO files VALUES(?, ?, ?, ?)", (identifier, sha, name, sheetID))
        fileDatabase.commit()


def setReachedPoints(config, sheetID, taskID, identifier, newPoints):
    pointsDatabase = getPointsTable(config)
    cursor = pointsDatabase.cursor()

    cursor.execute("SELECT reachedPoints FROM points WHERE sheetID = ? AND taskID = ? AND identifier = ?",
                   (sheetID, taskID, identifier))

    reachedPoints = cursor.fetchone()

    if reachedPoints:
        cursor.execute("UPDATE points SET reachedPoints = ? WHERE sheetID = ? AND taskID = ? AND identifier = ?",
                       (newPoints, sheetID, taskID, identifier,))
    else:
        cursor.execute("INSERT INTO points VALUES(?, ?, ?, ?)", (identifier, sheetID, taskID, newPoints))
    pointsDatabase.commit()


def setSheetNameForID(config, sheetID, oldName, newName):
    sheetDatabase = getSheetTable(config)
    sheetCursor = sheetDatabase.cursor()

    sheetCursor.execute("UPDATE sheets SET name = ? WHERE sheetID = ?", (newName, sheetID))
    sheetDatabase.commit()

    taskDatabase = getTaskTable(config)
    taskCursor = taskDatabase.cursor()

    taskCursor.execute("UPDATE tasks SET sheetID = ? WHERE sheetID = ?", (newName, oldName))
    taskDatabase.commit()


def setNewTaskForSheet(config, sheetID, taskName, taskDescription, taskPoints):
    taskDatabase = getTaskTable(config)
    taskCursor = taskDatabase.cursor()

    taskCursor.execute("""INSERT INTO tasks (sheetID, name, description, maxPoints)
                          VALUES(?, ?, ?, ?)""", (sheetID, taskName, taskDescription, taskPoints))

    taskDatabase.commit()


# Table getter methods

def getFileTable(config):
    fileDatabasePath = config("database_path")
    fileDatabase = sqlite3.connect(fileDatabasePath)
    cursor = fileDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS files
        (`identifier` text, `sha` text, `name` text, `sheetID` Integer);""")
    return fileDatabase


def getStatusTable(config):
    statusDatabasePath = config("database_path")
    statusDatabase = sqlite3.connect(statusDatabasePath)
    cursor = statusDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS status
        (`identifier` text, `sheetID` Integer, `status` text);""")
    return statusDatabase


def getPointsTable(config):
    pointsDatabasePath = config("database_path")
    pointsDatabase = sqlite3.connect(pointsDatabasePath)
    cursor = pointsDatabase.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS points
        (`identifier` text, `sheetID` Integer, `taskID` Integer, `reachedPoints` float);""")
    return pointsDatabase


def getSheetTable(config):
    sheetDatabasePath = config("database_path")
    sheetDatabase = sqlite3.connect(sheetDatabasePath)
    cursor = sheetDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sheets
        (`sheetID` Integer PRIMARY KEY AUTOINCREMENT, `editable` boolean, `name` text,
            `start` Integer, `end` Integer);""")
    return sheetDatabase


def getTaskTable(config):
    taskDatabasePath = config("database_path")
    taskDatabase = sqlite3.connect(taskDatabasePath)
    cursor = taskDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks
        (`sheetID` Integer, `taskID` Integer PRIMARY KEY AUTOINCREMENT, `name` text,
            `description` text, `maxPoints` float);""")
    return taskDatabase
