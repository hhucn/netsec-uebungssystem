from __future__ import unicode_literals

import logging
import sqlite3

from .sheet import Sheet
from .submission import Submission


def addFileToSubmission(config, submissionID, identifier, sha, name):
    # Add a file to the specified submission and identifier (student)

    fileDatabase = getFileTable(config)
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

    submissionDatabase = getSubmissionTable(config)
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

# Table getter methods


def getSheetTable(config):
    # Get the sheet table from the database
    sheetDatabasePath = config("database_path")
    sheetDatabase = sqlite3.connect(sheetDatabasePath)
    cursor = sheetDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sheets
        (`sheetID` Integer PRIMARY KEY AUTOINCREMENT,
         `editable` boolean,
         `name` text,
         `start` date,
         `end` date);""")
    return sheetDatabase


def getTaskTable(config):
    # Get the task table from the database
    taskDatabasePath = config("database_path")
    taskDatabase = sqlite3.connect(taskDatabasePath)
    cursor = taskDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks
        (`taskID` Integer PRIMARY KEY AUTOINCREMENT,
         `sheetID` Integer,
         `name` text,
         `description` text,
         `maxPoints` float);""")
    return taskDatabase


def getSubmissionTable(config):
    # Get the submission table from the database
    submissionDatabasePath = config("database_path")
    submissionDatabase = sqlite3.connect(submissionDatabasePath)
    cursor = submissionDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS submissions
        (`submissionID` Integer PRIMARY KEY AUTOINCREMENT,
         `taskID` Integer,
         `identifier` text,
         `points` text);""")
    return submissionDatabase


def getFileTable(config):
    # Get the file table from the database
    fileDatabasePath = config("database_path")
    fileDatabase = sqlite3.connect(fileDatabasePath)
    cursor = fileDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS files
        (`fileID` Integer PRIMARY KEY AUTOINCREMENT,
         `submissionID` Integer,
         `sha` text,
         `filename` text);""")
    return fileDatabase


# Object getter methods

def getSheets(config):
    sheetTable = getSheetTable(config)
    sheetCursor = sheetTable.cursor()

    sheetCursor.execute("SELECT sheetID, name, editable, start, end from sheets")
    rows = sheetCursor.fetchall()
    result = []

    for row in rows:
        sheetID, sheetName, editable, sheetStartDate, sheetEndDate = row
        result.append(Sheet(sheetID, sheetName, [], editable, sheetStartDate, sheetEndDate))

    return result


def getSubmissionForSheet(config, id):
    submissionTable = getSubmissionTable(config)
    submissionCursor = submissionTable.cursor()

    submissionCursor.execute("SELECT submissionID, taskID, identifier, points from submissions")
    rows = submissionCursor.fetchall()
    result = []

    for row in rows:
        submissionID, taskID, identifier, points = row
        result.append(Submission(submissionID, taskID, identifier, points))

    return result


def getSheetFromID(config, id):
    sheetTable = getSheetTable(config)
    sheetCursor = sheetTable.cursor()

    sheetCursor.execute("SELECT sheetID, editable, name, start, end from sheets")
    sheet = sheetCursor.fetchone()

    if sheet:
        sheetID, sheetName, editable, sheetStartDate, sheetEndDate = sheet
        return Sheet(sheetID, sheetName, [], editable, sheetStartDate, sheetEndDate)
