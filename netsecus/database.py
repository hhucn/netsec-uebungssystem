from __future__ import unicode_literals

import logging
import sqlite3

from .sheet import Sheet
from .submission import Submission
from .task import Task


def getTable(config, tableName):
    if not hasattr(config, "database"):
        databasePath = config("database_path")
        config.database = sqlite3.connect(databasePath)

    tableStructure = config("tableStructures.%s" % tableName)
    createStatement = "CREATE TABLE IF NOT EXISTS %s (%s);" % (tableName, tableStructure)

    cursor = config.database.cursor()
    cursor.execute(createStatement)

    return config.database


# Object getter methods

def getSheets(config):
    sheetTable = getTable(config, "sheets")
    sheetCursor = sheetTable.cursor()

    sheetCursor.execute("SELECT sheetID, name, editable, start, end FROM sheets")
    rows = sheetCursor.fetchall()
    result = []

    for row in rows:
        sheetID, sheetName, editable, sheetStartDate, sheetEndDate = row
        tasks = getTasksForSheet(config, sheetID)
        result.append(Sheet(sheetID, sheetName, tasks, editable, sheetStartDate, sheetEndDate))

    return result


def getSubmissionForSheet(config, id):
    submissionTable = getTable(config, "submissions")
    submissionCursor = submissionTable.cursor()

    submissionCursor.execute("SELECT submissionID, taskID, identifier, points FROM submissions")
    rows = submissionCursor.fetchall()
    result = []

    for row in rows:
        submissionID, taskID, identifier, points = row
        result.append(Submission(submissionID, taskID, identifier, points))

    return result


def getSheetFromID(config, id):
    sheetTable = getTable(config, "sheets")
    sheetCursor = sheetTable.cursor()

    sheetCursor.execute("SELECT sheetID, editable, name, start, end FROM sheets WHERE sheetID = ?", (id, ))
    sheet = sheetCursor.fetchone()

    if sheet:
        sheetID, editable, sheetName, sheetStartDate, sheetEndDate = sheet
        tasks = getTasksForSheet(config, id)
        return Sheet(sheetID, sheetName, tasks, editable, sheetStartDate, sheetEndDate)


def getTaskFromID(config, id):
    taskTable = getTable(config, "tasks")
    taskCursor = taskTable.cursor()

    taskCursor.execute("SELECT sheetID, name, description, maxPoints FROM tasks WHERE taskID = ?", (id, ))
    task = taskCursor.fetchone()

    if task:
        sheetID, name, description, maxPoints = task
        return Task(id, sheetID, name, description, maxPoints)


def getTasksForSheet(config, id):
    taskTable = getTable(config, "tasks")
    taskCursor = taskTable.cursor()

    taskCursor.execute("SELECT taskID, name, description, maxPoints FROM tasks WHERE sheetID = ?", (id, ))
    tasks = taskCursor.fetchall()

    result = []

    for task in tasks:
        taskID, name, description, maxPoints = task
        result.append(Task(taskID, id, name, description, maxPoints))

    return result


# Object setter/misc. functions

def setSheet(config, name):
    sheetTable = getTable(config, "sheets")
    sheetCursor = sheetTable.cursor()

    sheetCursor.execute("INSERT INTO sheets (name) VALUES (?)", (name, ))
    sheetTable.commit()


def setNewTaskForSheet(config, sheetID, name, description, maxPoints):
    taskTable = getTable(config, "tasks")
    taskCursor = taskTable.cursor()

    taskCursor.execute("INSERT INTO tasks (sheetID, name, description, maxPoints) VALUES(?,?,?,?)",
                       (sheetID, name, description, maxPoints))
    taskTable.commit()


def replaceTask(config, id, task):
    taskTable = getTable(config, "tasks")
    taskCursor = taskTable.cursor()

    name = task.name
    desc = task.description
    maxPoints = task.maxPoints

    taskCursor.execute("UPDATE tasks SET name=? AND description=? and maxPoints=? WHERE taskID=?",
                       (name, desc, maxPoints, id))
    taskTable.commit()


def deleteTask(config, id):
    taskTable = getTable(config, "tasks")
    taskCursor = taskTable.cursor()

    taskCursor.execute("DELETE FROM tasks WHERE taskID = ?", (id, ))
    taskTable.commit()


def addFileToSubmission(config, submissionID, identifier, sha, name):
    # Add a file to the specified submission and identifier (student)

    fileDatabase = getTable(config, "files")
    cursor = fileDatabase.cursor()

    cursor.execute("""SELECT fileID FROM files
                      WHERE submissionID = ?
                      AND identifier = ?
                      AND sha = ?""",
                   (submissionID, identifier, sha))

    if cursor.fetchone():
        # File is sent twice in one mail (realistic) OR the SHA of two different
        # files collided (not that realistic...)
        logging.debug("Two files with the same checksum submitted by %s"
                      % identifier)
    else:
        cursor.execute("""INSERT INTO files(submissionID, identifier, sha)
                          VALUES(?, ?, ?)""", (submissionID, identifier, sha))
        fileDatabase.submit()


def submissionForTaskAndIdentifier(config, taskID, identifier, points):
    # Get the submission ID for the specified task and identifier (student)
    # if it does not exist, create it.

    submissionDatabase = getTable(config, "submissions")
    cursor = submissionDatabase.cursor()

    cursor.execute("""SELECT submissionID FROM submissions
                      WHERE taskID = ? AND identifier = ? AND points = ?""",
                   (taskID, identifier, points))

    existingSubmissionID = cursor.fetchone()

    if existingSubmissionID:
        return existingSubmissionID[0]  # just return submissionID
    else:
        # No submission for this task exists from this identifier
        cursor.execute("""INSERT INTO
                          submissions(taskID, identifier, points)
                          VALUES(?, ?, ?)""", (taskID, identifier,
                       points))
        return cursor.lastrowid
