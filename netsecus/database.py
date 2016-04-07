from __future__ import unicode_literals

import sqlite3

from .file import File
from .sheet import Sheet
from .student import Student


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
                `time` BIGINT,
                `files_path` text
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

    def commit(self):
        return self.database.commit()
