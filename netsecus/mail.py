from __future__ import unicode_literals


class Mail(object):

    def __init__(self, uid, var, text):
        self.uid = uid
        self.variables = var
        self.text = text
        self.variables["MAILFROM"] = text["From"]
        self.variables["MAILDATE"] = text["Date"]
        self.variables["MAILRECEIVED"] = text["Received"]
