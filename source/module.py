#
#  module.py
#  Unbound Bible Python Edition
#

import sqlite3

class Module:
    database     = None
    filePath     = ""
    fileName     = ""
    format       = "unbound"

    name         = ""
    abbr         = ""
    copyright    = ""
    info         = ""
    filetype     = ""

#   firstVerse   = Verse()
    language     = "en"
    rightToLeft  = True

    connected    = False
    loaded       = False
    strong       = False
    embedded     = False
    footnotes    = False
    interlinear  = False
    embtitles    = False

    def __init__(self, atPath: str):
        self.filePath = atPath
        self.fileName = atPath#.lastPathComponent
        ext = "unbound" #filePath.pathExtension
        if ext == "mybible" or ext == "bbli": format = "mysword"
        self.openDatabase()
##      if !connected { return nil }

    def encodeID(id: int) -> int:
        return unbound2mybible(id) if format == "mybible" else id

    def decodeID(id: int) -> int:
        return mybible2unbound(id) if format == "mybible" else id

    def openDatabase(self):
        self.filePath = "bibles/rstw.unbound"
        self.database = sqlite3.connect(self.filePath)
        cursor = self.database.cursor()

        sql = "SELECT * FROM Bible WHERE book=1 AND chapter=1"
        cursor.execute(sql)
        print(cursor.fetchall()) # or use fetchone()
        self.database.close
##        if !database!.open() { return }
##        if database!.tableExists("info") { format = .mybible }

atPath = "bibles/rstw.unbound"
module = Module(atPath)
