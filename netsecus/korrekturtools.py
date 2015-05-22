from __future__ import unicode_literals

import os
import logging

from . import helper

def readStatus(config, student):
    student = student.lower()
    path = config("attachment_path")

    if not os.path.exists(path):
        return

    path = os.path.join(path, student)

    if not os.path.exists(path):
        return "Student ohne Abgabe"

    path = os.path.join(path, "korrekturstatus.txt")

    if not os.path.exists(path):
        return "Unbearbeitet"

    statusfile = open(path, "r")
    status = statusfile.read()
    statusfile.close()
    return status


def writeStatus(config, student, status):
    student = student.lower()
    status = status.lower()

    path = os.path.join(config("attachment_path"), student)

    if not os.path.exists(path):
        logging.error("Requested student '%s' hasn't submitted anything yet.")
        return

    path = os.path.join(path, "korrekturstatus.txt")

    with open(path, "w") as statusfile:
        statusfile.write(status)
