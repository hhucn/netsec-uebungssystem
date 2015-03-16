from __future__ import unicode_literals

import os

from . import helper



def readStatus(student):
    student = student.lower()

    if not os.path.exists("attachments"):
        return

    if not os.path.exists(os.path.join("attachments", student)):
        return "Student ohne Abgabe"

    if not os.path.exists(os.path.join("attachments", student, "korrekturstatus.txt")):
        return "Unbearbeitet"
    statusfile = open(os.path.join("attachments", student, "korrekturstatus.txt"), "r")
    status = statusfile.read()
    statusfile.close()
    return status


def writeStatus(student, status):
    student = student.lower()
    status = status.lower()

    if not os.path.exists(os.path.join("attachments", student)):
        logging.error("Requested student '%s' hasn't submitted anything yet.")
        return
    statusfile = open(os.path.join("attachments", student, "korrekturstatus.txt"), "w")
    statusfile.write(status)
    statusfile.close()
