from __future__ import unicode_literals

import logging
import sqlite3

from .file import File
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
                `filename` text,
                `path` text
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `students` (
                `identifier` text,
                `alias` text,
                `deleted` boolean
            )""")

    def getSheets(self):
        self.cursor.execute("SELECT sheetID, end, deleted FROM sheets")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            sheetID, sheetEndDate, deleted = row
            tasks = self.getTasksForSheet(sheetID)
            result.append(Sheet(sheetID, tasks, sheetEndDate, deleted))

        return result

    def getStudent(self, id):
        self.cursor.execute("SELECT identifier, alias, deleted FROM students WHERE identifier = ?", (id, ))
        identifier, alias, deleted = self.cursor.fetchone()
        if identifier:
            return Student(identifier, alias, deleted)

    def getStudents(self):
        self.cursor.execute("SELECT identifier, alias, deleted FROM students")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            identifier, alias, deleted = row
            result.append(Student(identifier, alias, deleted))

        return result

    def createStudent(self, id):
        self.cursor.execute("INSERT INTO students (identifier, deleted) VALUES (?, 0)", (id, ))
        self.database.commit()

    def deleteStudent(self, id):
        self.cursor.execute("UPDATE students SET deleted = 1 WHERE identifier = ?", (id, ))
        self.database.commit()

    def restoreStudent(self, id):
        self.cursor.execute("UPDATE students SET deleted = 0 WHERE identifier = ?", (id, ))
        self.database.commit()

    def setAliasForStudent(self, id, alias):
        self.cursor.execute("UPDATE students SET alias = ? WHERE identifier = ?", (alias, id))
        self.database.commit()

    def resolveAlias(self, alias):
        self.cursor.execute("SELECT identifier FROM students WHERE alias = ?", (alias,))
        return self.cursor.fetchone()

    def createSubmission(self, sheetID, identifier):
        self.cursor.execute("INSERT INTO submissions (sheetID, identifier) VALUES (?, ?)", (sheetID, identifier))
        self.database.commit()
        self.cursor.execute("SELECT last_insert_rowid()")
        return self.cursor.fetchone()[0]  # just return id, not (id, )

    def getSubmissionsForStudent(self, identifier):
        self.cursor.execute("SELECT submissionID, sheetID, points FROM submissions WHERE identifier = ?", (identifier,))
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            submissionID, sheetID, points = row
            result.append(Submission(submissionID, sheetID, identifier, points))

        return result

    def getAllSubmissions(self):
        self.cursor.execute("SELECT submissionID, sheetID, identifier, points FROM submissions")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            submissionID, sheetID, identifier, points = row
            result.append(Submission(submissionID, sheetID, identifier, points))

        return result

    def getSubmissionFromID(self, submissionID):
        self.cursor.execute("SELECT sheetID, identifier, points FROM submissions")
        sheetID, identifier, points = self.cursor.fetchone()

        return Submission(submissionID, sheetID, identifier, points)

    def getSheetFromID(self, id):
        self.cursor.execute("SELECT sheetID, end, deleted FROM sheets WHERE sheetID = ?", (id, ))
        sheet = self.cursor.fetchone()

        if sheet:
            sheetID, sheetEndDate, deleted = sheet
            tasks = self.getTasksForSheet(id)
            return Sheet(sheetID, tasks, sheetEndDate, deleted)

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

    def addFileToSubmission(self, submissionID, sha, name, path):
        self.cursor.execute("""INSERT INTO files(submissionID, sha, filename, path)
                               VALUES(?, ?, ?, ?)""", (submissionID, sha, name, path))
        self.database.commit()

    def getFilesForSubmission(self, submissionID):
        self.cursor.execute("SELECT fileID, sha, filename, path FROM files WHERE submissionID = ?", (submissionID, ))
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            fileID, sha, filename, path = row
            result.append(File(fileID, submissionID, sha, filename, path))

        return result
