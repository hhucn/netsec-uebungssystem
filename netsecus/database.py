from __future__ import unicode_literals

import logging
import sqlite3

from .sheet import Sheet
from .submission import Submission
from .task import Task


class Database(object):
    def __init__(self, config):
        databasePath = config("database_path")
        self.database = sqlite3.connect(databasePath)
        self.cursor = self.database.cursor()
        self.createTables()

    def createTables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `sheetID` (`sheetID` Integer PRIMARY KEY
                            AUTOINCREMENT, `editable` boolean, `name` text, `start` date, `end` date)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `taskID` (`taskID` Integer PRIMARY KEY
                            AUTOINCREMENT, `sheetID` Integer, `name` text, `maxPoints` float)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `submissionID` (`submissionID` Integer PRIMARY KEY
                            AUTOINCREMENT, `taskID` Integer, `identifier` text, `points` text)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `fileID` (`fileID` Integer PRIMARY KEY
                            AUTOINCREMENT, `submissionID` Integer, `sha` text, `filename` text)""")

    def getSheets(self):
        self.cursor.execute("SELECT sheetID, name, editable, start, end FROM sheets")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            sheetID, sheetName, editable, sheetStartDate, sheetEndDate = row
            tasks = self.getTasksForSheet(sheetID)
            result.append(Sheet(sheetID, sheetName, tasks, editable, sheetStartDate, sheetEndDate))

        return result

    def getSubmissionForSheet(self, id):
        self.cursor.execute("SELECT submissionID, taskID, identifier, points FROM submissions")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            submissionID, taskID, identifier, points = row
            result.append(Submission(submissionID, taskID, identifier, points))

        return result

    def getSheetFromID(self, id):
        self.cursor.execute("SELECT sheetID, editable, name, start, end FROM sheets WHERE sheetID = ?", (id, ))
        sheet = self.cursor.fetchone()

        if sheet:
            sheetID, editable, sheetName, sheetStartDate, sheetEndDate = sheet
            tasks = self.getTasksForSheet(id)
            return Sheet(sheetID, sheetName, tasks, editable, sheetStartDate, sheetEndDate)

    def getTaskFromID(self, id):
        self.cursor.execute("SELECT sheetID, name, maxPoints FROM tasks WHERE taskID = ?", (id, ))
        task = self.cursor.fetchone()

        if task:
            sheetID, name, maxPoints = task
            return Task(id, sheetID, name, maxPoints)

    def getTasksForSheet(self, id):
        self.cursor.execute("SELECT taskID, name, maxPoints FROM tasks WHERE sheetID = ?", (id, ))
        tasks = self.cursor.fetchall()

        result = []

        for task in tasks:
            taskID, name, maxPoints = task
            result.append(Task(taskID, id, name, maxPoints))

        return result

    def createSheet(self, name):
        self.cursor.execute("INSERT INTO sheets (name) VALUES (?)", (name, ))
        self.database.commit()

    def setNewTaskForSheet(self, sheetID, name, maxPoints):
        self.cursor.execute("INSERT INTO tasks (sheetID, name, maxPoints) VALUES(?,?,?,?)", (sheetID, name, maxPoints))
        self.database.commit()

    def replaceTask(self, id, task):
        name = task.name
        maxPoints = task.maxPoints

        self.cursor.execute("UPDATE tasks SET name=? AND maxPoints=? WHERE taskID=?", (name, maxPoints, id))
        self.database.commit()

    def deleteTask(self, id):
        self.cursor.execute("DELETE FROM tasks WHERE taskID = ?", (id, ))
        self.database.commit()
        self.database.commit()

    def createTask(self, sheetID, name, maxPoints):
        self.cursor.execute("INSERT INTO tasks (sheetID, name, maxPoints) VALUES(?,?,?)",
                            (sheetID, name, maxPoints))
        self.database.commit()

    def addFileToSubmission(self, submissionID, identifier, sha, name):
        # Add a file to the specified submission and identifier (student)
        self.cursor.execute("""SELECT fileID FROM files
                            WHERE submissionID = ?
                            AND identifier = ?
                            AND sha = ?""",
                            (submissionID, identifier, sha))

        if self.cursor.fetchone():
            # File is sent twice in one mail (realistic) OR the SHA of two different
            # files collided (not that realistic...)
            logging.debug("Two files with the same checksum submitted by %s"
                          % identifier)
        else:
            self.cursor.execute("""INSERT INTO files(submissionID, identifier, sha)
                              VALUES(?, ?, ?)""", (submissionID, identifier, sha))
            self.database.submit()

    def submissionForTaskAndIdentifier(self, taskID, identifier, points):
        # Get the submission ID for the specified task and identifier (student)
        # if it does not exist, create it.
        self.cursor.execute("""SELECT submissionID FROM submissions
                            WHERE taskID = ? AND identifier = ? AND points = ?""",
                            (taskID, identifier, points))

        existingSubmissionID = self.cursor.fetchone()

        if existingSubmissionID:
            return existingSubmissionID[0]  # just return submissionID
        else:
            # No submission for this task exists from this identifier
            self.cursor.execute("""INSERT INTO
                                submissions(taskID, identifier, points)
                                VALUES(?, ?, ?)""", (taskID, identifier,
                                points))
            return self.cursor.lastrowid
