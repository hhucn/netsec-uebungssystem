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
            tasks = self.getTasksForSheet(id)
            result.append(Sheet(id, tasks, end, deleted))

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

    def createStudent(self, student_id):
        self.cursor.execute("INSERT INTO student VALUES (?)", (student_id, ))
        self.database.commit()

    def addAliasForStudent(self, student_id, alias):
        self.cursor.execute("INSERT INTO alias VALUES(?,?)", (student_id, alias))
        self.database.commit()

    def deleteAliasForStudent(self, id, alias):
        self.cursor.execute("DELETE FROM alias WHERE student_id = ? AND alias = ?", (id, alias))
        self.database.commit()

    def getAliasesForStudent(self, student_id):
        self.cursor.execute("SELECT alias FROM alias WHERE student_id = ?", (student_id, ))
        rows = self.cursor.fetchall()
        result = []

        for row in rows:
            result.append(row[0])  # get alias

        return result

    def resolveAlias(self, alias):
        self.cursor.execute("SELECT student_id FROM alias WHERE alias = ?", (alias,))
        foundAlias = self.cursor.fetchone()

        if not foundAlias:
            logging.debug("Couldn't resolve alias '%s'" % alias)
            return alias
        return foundAlias[0]  # if the line exists, "foundAlias" contains a tuple

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

    def getSheetFromID(self, sheet_id):
        self.cursor.execute("SELECT end, deleted FROM sheet WHERE id = ?", (sheet_id, ))
        sheet = self.cursor.fetchone()

        if sheet:
            end, deleted = sheet
            tasks = self.getTasksForSheet(sheet_id)
            return Sheet(sheet_id, tasks, end, deleted)

    def getTaskFromID(self, id):
        self.cursor.execute("SELECT sheetID, name, maxPoints FROM tasks WHERE taskID = ?", (id, ))
        task = self.cursor.fetchone()

        if task:
            sheetID, name, maxPoints = task
            return Task(id, sheetID, name, maxPoints)

    def getTasksForSheet(self, sheet_id):
        self.cursor.execute("SELECT id, name, decipoints FROM task WHERE sheet_id = ?", (sheet_id, ))
        tasks = self.cursor.fetchall()

        result = []

        for task in tasks:
            id, name, decipoints = task
            result.append(Task(id, sheet_id, name, decipoints))

        return result

    def createSheet(self):
        self.cursor.execute("INSERT INTO sheet DEFAULT VALUES")
        self.database.commit()

    def deleteSheet(self, sheet_id):
        self.cursor.execute("UPDATE sheet SET deleted = 1 WHERE id = ?", (sheet_id, ))
        self.database.commit()

    def restoreSheet(self, sheet_id):
        self.cursor.execute("UPDATE sheet SET deleted = 0 WHERE id = ?", (sheet_id, ))
        self.database.commit()

    def editEnd(self, sheet_id, end):
        self.cursor.execute("UPDATE sheet SET end=? WHERE id = ?", (end, sheet_id))
        self.database.commit()

    def setNewTaskForSheet(self, sheet_id, name, decipoints):
        self.cursor.execute("INSERT INTO task (sheet_id, name, decipoints) VALUES(?,?,?)", (sheet_id, name, decipoints))
        self.database.commit()

    def setNameForTask(self, task_id, name):
        self.cursor.execute("UPDATE task SET name=? WHERE id=?", (name, task_id))
        self.database.commit()

    def setPointsForTask(self, task_id, decipoints):
        self.cursor.execute("UPDATE task SET decipoints=? WHERE id=?", (decipoints, task_id))
        self.database.commit()

    def deleteTask(self, task_id):
        self.cursor.execute("DELETE FROM task WHERE id = ?", (task_id, ))
        self.database.commit()

    def createTask(self, sheet_id, name, decipoints):
        self.cursor.execute("INSERT INTO tasks (sheet_id, name, decipoints) VALUES(?,?,?)",
                            (sheet_id, name, decipoints))
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
