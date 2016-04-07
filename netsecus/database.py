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
            """CREATE TABLE IF NOT EXISTS `sheet` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `end` BIGINT,
                `deleted` boolean
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `task` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `sheet_id` INTEGER REFERENCES sheet(id),
                `name` text,
                `decipoints` INTEGER
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `submission` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `sheet_id` INTEGER REFERENCES sheet(id),
                `student_id` INTEGER REFERENCES student(id),
                `time` BIGINT
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `grading` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `submission_id` INTEGER REFERENCES submission(id),
                `comment` TEXT,
                `time` BIGINT,
                `decipoints` INTEGER
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `file` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `submission_id` INTEGER REFERENCES submission(id),
                `hash` text,
                `filename` text
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `student` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT
            )""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `alias` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `student_id` INTEGER REFERENCES student(id),
                `alias` text UNIQUE
            )""")

    def getSheets(self):
        self.cursor.execute("SELECT id, end, deleted FROM sheet")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            id, end, deleted = row
            result.append(Sheet(id, end, deleted))

        return result

    def getStudent(self, id):
        aliases = self.getAliasesForStudent(identifier)
        return Student(identifier, aliases)

    def getStudents(self):
        self.cursor.execute("SELECT id FROM student")
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            student_id = row[0]
            aliases = self.getAliasesForStudent(student_id)
            result.append(Student(student_id, aliases))

        return result

    def createSubmission(self, sheetID, identifier):
        self.cursor.execute("INSERT INTO submissions (sheetID, identifier) VALUES (?, ?)", (sheetID, identifier))
        self.database.commit()
        self.cursor.execute("SELECT last_insert_rowid()")
        return self.cursor.fetchone()[0]  # just return id, not (id, )

    def getSubmissionsForStudent(self, student_id):
        self.cursor.execute("SELECT id, sheet_id, time FROM submission WHERE student_id = ?", (student_id,))
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            id, sheet_id, time = row
            result.append(Submission(id, sheet_id, student_id, time))

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

    def deleteSheet(self, sheet_id):
        self.cursor.execute("UPDATE sheet SET deleted = 1 WHERE id = ?", (sheet_id, ))
        self.database.commit()

    def restoreSheet(self, sheet_id):
        self.cursor.execute("UPDATE sheet SET deleted = 0 WHERE id = ?", (sheet_id, ))
        self.database.commit()

    def editEnd(self, sheet_id, end):
        self.cursor.execute("UPDATE sheet SET end=? WHERE id = ?", (end, sheet_id))
        self.database.commit()

    def addFileToSubmission(self, submission_id, hash, filename):
        self.cursor.execute("""INSERT INTO file (submission_id, hash, filename)
                               VALUES(?, ?, ?)""", (submission_id, hash, filename))
        self.database.commit()

    def getFilesForSubmission(self, submission_id):
        self.cursor.execute("SELECT id, hash, filename FROM file WHERE submission_id = ?", (submission_id, ))
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            id, hash, filename = row
            result.append(File(id, hash, filename))

        return result

    def commit(self):
        return self.database.commit()
