#
#  module.py
#  Unbound Bible Python Edition
#

import sqlite3
from data import *

class Module:
    database     = None
    cursor       = None
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
        if ext == "mybible" or ext == "bbli": self.format = "mysword"
        self.openDatabase()

    def encodeID(id: int) -> int:
#       return unbound2mybible(id) if self.format == "mybible" else id
        return id

    def decodeID(id: int) -> int:
#       return mybible2unbound(id) if self.format == "mybible" else id
        return id

    def tableExists(cursor, tablename) -> bool:
        query = f"PRAGMA table_info({tablename})" # case insensitive method
        cursor.execute(query)
        return cursor.fetchone() != None

    def dict_factory(cursor, row) -> dict:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0].capitalize()] = row[idx]
        return d

    def openDatabase(self):
        try:
            self.database = sqlite3.connect(self.filePath)
            self.database.row_factory = Module.dict_factory
            self.cursor = self.database.cursor()
        except:
            return

        if Module.tableExists(self.cursor, "info"): format = "mybible"

        if self.format == "unbound" or self.format == "mysword":
            query = "select * from Details"
            try:
                self.cursor.execute(query)
                r = self.cursor.fetchone()
                r = dict(r)

                self.info      = r.get("Information",  "")
                self.info      = r.get("Description", self.info)
                self.name      = r.get("Title",       self.info)
                self.abbr      = r.get("Abbreviation", "")
                self.copyright = r.get("Copyright",    "")
                self.language  = r.get("Language",     "")
                self.strong    = r.get("Strong",       "")
                self.embedded  = r.get("Embedded",     "")

                self.connected = True
                print(self.info)
            except:
                print("exception")

        if self.format == "mybible":
            try:
                query = "select * from info"
                self.cursor.execute(query)
                r = self.cursor.fetchall()
                r = dict(r)

                self.name     = r.get("Description",   "")
                self.info     = r.get("Detailed_info", "")
                self.language = r.get("Language",      "")

                if r.get("Is_strong"   , "") == "true": self.strong    = True
                if r.get("Is_footnotes", "") == "true": self.footnotes = True

                self.connected = True
                print(self.name)
            except:
                print("exception")

        if self.connected:
            if not self.name: self.name = self.fileName
#           self.rightToLeft = getRightToLeft(self.language)
#           info = info.removeTags

class Bible(Module):

    def __init__(self, atPath: str):
        Module.__init__(self, atPath)

        if format == "mybible":
#           z = mybibleAlias
#           if !database!.tableExists(z.titles) { z.titles = "books" }
            pass

#        embtitles = database!.tableExists(z.titles)
#        if connected && !database!.tableExists(z.bible) { return nil }

    def getChapter(self, verse: Verse) -> [str]: ## verse: Verse
        id = Module.encodeID(verse.book)
##      let nt = isNewTestament(verse.book)
##      let query = "select * from \(z.bible) where \(z.book) = \(id) and \(z.chapter) = \(verse.chapter)"
        query = f"SELECT * FROM Bible WHERE book={id} AND chapter={verse.chapter}"

        try:
            self.cursor.execute(query)
            r = self.cursor.fetchall()
            result = []
            for d in r:
                text = d.get("Scripture", "")
#               text = preparation(text, format: format, nt: nt, purge: false)
                result.append(text)
            return result
        except:
            print("exception")
            return []

path = "bibles/rstw.unbound"
#path = "bibles/AMP.SQLite3"
bible = Bible(path)

verse = Verse()
verse.book    = 40
verse.chapter = 2
verse.number  = 1
verse.count   = 0

out = bible.getChapter(verse)
print(out)

