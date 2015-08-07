from __future__ import unicode_literals

import sqlite3

from .sheet import Sheet
from .task import Task


# Table getter methods

def getSheetTable(config):
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
    fileDatabasePath = config("database_path")
    fileDatabase = sqlite3.connect(fileDatabasePath)
    cursor = fileDatabase.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS files
        (`fileID` Integer PRIMARY KEY AUTOINCREMENT,
         `submissionID` Integer,
         `sha` text,
         `filename` text);""")
    return fileDatabase
