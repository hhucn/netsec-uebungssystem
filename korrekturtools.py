import os


def readStatus(student):
    student = student.lower()

    if not os.path.exists("attachments"):
        return

    if not os.path.exists("attachments/" + student):
        return "Student ohne Abgabe"

    if not os.path.exists("attachments/%s/korrekturstatus.txt" % student):
        return "Unbearbeitet"
    statusfile = open("attachments/%s/korrekturstatus.txt" % student, "r")
    status = statusfile.read()
    statusfile.close()
    return status


def writeStatus(student, status):
    student = student.lower()
    status = status.lower()

    if not os.path.exists("attachments"):
        return

    if not os.path.exists("attachments/" + student):
        return
    statusfile = open("attachments/%s/korrekturstatus.txt" % student, "w")
    statusfile.write(status)
    statusfile.close()
