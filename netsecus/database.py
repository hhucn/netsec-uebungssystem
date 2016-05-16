from __future__ import unicode_literals

import sqlite3


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

        # Legacy table - remove
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `grading` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `submission_id` INTEGER REFERENCES submission(id),
                `task_id` INTEGER REFERENCES task(id),
                `comment` TEXT,
                `time` BIGINT,
                `decipoints` INTEGER,
                `grader` TEXT
            )""")

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `grading_result` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `student_id` INTEGER REFERENCES student(id),
                `sheet_id` INTEGER REFERENCES sheet(id),
                `submission_id` INTEGER REFERENCES submission(id),
                `reviews_json` TEXT,
                `decipoints` INTEGER,
                `grader` TEXT,
                `sent_mail_uid` INTEGER,
                `status` TEXT
            )""")

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `file` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `submission_id` INTEGER REFERENCES submission(id),
                `hash` text,
                `filename` text,
                `size` BIGINT
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
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `assignment` (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `grader` TEXT,
                `sheet_id` INTEGER REFERENCES sheet(id),
                `student_id` INTEGER REFERENCES student(id)
            )""")

    def commit(self):
        return self.database.commit()
