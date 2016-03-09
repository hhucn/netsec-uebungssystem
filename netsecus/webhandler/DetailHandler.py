from __future__ import unicode_literals

from .NetsecHandler import NetsecHandler

class DetailHandler(NetsecHandler):
    def get(self):
        uri = self.request.uri.split("/")
        identifier = uri[2:][0]  # remove empty element and "detail", get student ID

        files = []

        attachmentPath = os.path.join(self.application.config("attachment_path"), helper.escapePath(identifier))
        if os.path.exists(attachmentPath):
            for entry in os.listdir(attachmentPath):
                if entry[0] != ".":
                    pathToFile = os.path.join(attachmentPath, entry)
                    fileHash, name = entry.split(" ", 1)
                    filesize = os.path.getsize(pathToFile) / 1024
                    fileDateTimestamp = os.path.getmtime(pathToFile)
                    fileDateTime = datetime.fromtimestamp(fileDateTimestamp).strftime("%Y-%m-%d %H:%M:%S %z")

                    if filesize == 0:
                        filesize = 1

                    files.append({
                        "name": name,
                        "size": "%i KB" % filesize,
                        "date": fileDateTime,
                        "hash": fileHash
                        })
            self.render('detail', {'identifier': identifier, 'files': files,
                                   'korrekturstatus': database.getStatus(self.application.config, identifier),
                                   'sheets': database.getSheets(self.application.config, identifier)})
        else:
            logging.error("Specified attachment path ('%s') does not exist." % attachmentPath)
            self.redirect("/")
