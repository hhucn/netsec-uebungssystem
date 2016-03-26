from __future__ import unicode_literals

import logging
import sqlite3

from .sheet import Sheet
from .submission import Submission
from .student import Student
from .task import Task


class Database(object):
    def __init__(self, config):
        databasePath = config("database_path")
        self.database = sqlite3.connect(databasePath)
        self.cursor = self.database.cursor()
        self.createTables()

    def createTables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `sheets` (
                `sheetID` INTEGER PRIMARY KEY,
                `editable` boolean,
                `end` date,
                `deleted` boolean
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `tasks` (
                `taskID` INTEGER PRIMARY KEY AUTOINCREMENT,
                `sheetID` INTEGER,
                `name` text,
                `maxPoints` float
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `submissions` (
                `submissionID` INTEGER PRIMARY KEY AUTOINCREMENT,
                `sheetID` INTEGER,
                `identifier` text,
                `points` text
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `files` (
                `fileID` INTEGER PRIMARY KEY AUTOINCREMENT,
                `submissionID` INTEGER,
                `sha` text,
                `filename` text
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `alias` (
                `alias` text,
                `identifier` text
            )""")

    def getSheets(self):
        self.cursor.execute("SELECT sheetID, editable, end, deleted FROM sheets")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            sheetID, editable, sheetEndDate, deleted = row
            tasks = self.getTasksForSheet(sheetID)
            result.append(Sheet(sheetID, tasks, editable, sheetEndDate, deleted))

        return result

    def getStudents(self):
        self.cursor.execute("SELECT identifier, alias FROM alias")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            identifier, alias = row
            exists = False
            for student in result:
                if student.identifier == identifier:
                    student.alias.append(alias)
                    exists = True
                    break
            if not exists:
                result.append(Student(identifier, alias))

        return result

    def resolveAlias(self, alias):
        self.cursor.execute("SELECT identifier FROM alias WHERE alias = ?", (alias,))
        return self.cursor.fetchone()

    def createSubmission(self, sheetID, identifier):
        self.cursor.execute("INSERT INTO submissions (sheetID, identifier) VALUES (?, ?)", (sheetID, identifier))
        self.database.commit()

    def getAllSubmissions(self):
        self.cursor.execute("SELECT submissionID, sheetID, identifier, points FROM submissions")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            submissionID, sheetID, identifier, points = row
            result.append(Submission(submissionID, sheetID, identifier, points))

        return result

    def getSheetFromID(self, id):
        self.cursor.execute("SELECT sheetID, editable, end, deleted FROM sheets WHERE sheetID = ?", (id, ))
        sheet = self.cursor.fetchone()

        if sheet:
            sheetID, editable, sheetEndDate, deleted = sheet
            tasks = self.getTasksForSheet(id)
            return Sheet(sheetID, tasks, editable, sheetEndDate, deleted)

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

    def createSheet(self):
        self.cursor.execute("INSERT INTO sheets DEFAULT VALUES")
        self.database.commit()

    def deleteSheet(self, sheetID):
        self.cursor.execute("UPDATE sheets SET deleted = 1 WHERE sheetID = ?", (sheetID, ))
        self.database.commit()

    def restoreSheet(self, sheetID):
        self.cursor.execute("UPDATE sheets SET deleted = 0 WHERE sheetID = ?", (sheetID, ))
        self.database.commit()

    def editEnd(self, sheetID, end):
        self.cursor.execute("UPDATE sheets SET end=? WHERE sheetID = ?", (end, sheetID, ))
        self.database.commit()

    def setNewTaskForSheet(self, sheetID, name, maxPoints):
        self.cursor.execute("INSERT INTO tasks (sheetID, name, maxPoints) VALUES(?,?,?,?)", (sheetID, name, maxPoints))
        self.database.commit()

    def setNameForTask(self, id, name):
        self.cursor.execute("UPDATE tasks SET name=? WHERE taskID=?", (name, id))
        self.database.commit()

    def setPointsForTask(self, id, points):
        self.cursor.execute("UPDATE tasks SET maxPoints=? WHERE taskID=?", (points, id))
        self.database.commit()

    def deleteTask(self, id):
        self.cursor.execute("DELETE FROM tasks WHERE taskID = ?", (id, ))
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
