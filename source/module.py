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

    firstVerse   = Verse()
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

    def encodeID(format: str, id: int) -> int:
        return unbound2mybible(id) if format == "mybible" else id

    def decodeID(format: str, id: int) -> int:
        return mybible2unbound(id) if format == "mybible" else id

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

        if Module.tableExists(self.cursor, "info"): self.format = "mybible"

        if self.format == "unbound" or self.format == "mysword":
            query = "select * from Details"
            try:
                self.cursor.execute(query)
                row = self.cursor.fetchone()

                self.info      = row.get("Information",  "")
                self.info      = row.get("Description", self.info)
                self.name      = row.get("Title",       self.info)
                self.abbr      = row.get("Abbreviation", "")
                self.copyright = row.get("Copyright",    "")
                self.language  = row.get("Language",     "")
                self.strong    = row.get("Strong",       "")
                self.embedded  = row.get("Embedded",     "")

                self.connected = True
                print(self.info)
            except:
                print("exception")

        if self.format == "mybible":
            try:
                query = "select * from info"
                self.cursor.execute(query)
                rows = self.cursor.fetchall()

                for row in rows:
                    name  = row.get("Name", "").lower()
                    value = row.get("Value", "")

                    if name == "description"  : self.name = value
                    if name == "detailed_info": self.info = value
                    if name == "language"     : self.language = value

                    if value.lower() == "true":
                        if name == "strong_numbers": self.strong = True
                        if name == "is_strong"     : self.strong = True
                        if name == "is_footnotes"  : self.footnotes = True

                self.connected = True
                print(self.name)
            except:
                print("exception")

        if self.connected:
            if not self.name: self.name = self.fileName
#           self.rightToLeft = getRightToLeft(self.language)
#           info = info.removeTags

class Bible(Module):
    books = [Book()]
    titles = [str]
    z = unboundAlias()

    def __init__(self, atPath: str):
        super().__init__(atPath)

        print(self.z.bible)
        if self.format == "mybible":
            self.z = mybibleAlias()
            print(self.z.bible)
#           if !database!.tableExists(z.titles) { z.titles = "books" }
            pass

#        embtitles = database!.tableExists(z.titles)
#        if connected && !database!.tableExists(z.bible) { return nil }

    def loadDatabase(self):
        if self.loaded: return
        query = f"SELECT DISTINCT {self.z.book} FROM {self.z.bible}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            for row in rows:
                id = row.get(f"{self.z.book}".capitalize(), 0)
                if type(id) is int:
                    if id > 0:
                        book = Book()
                        book.number = Module.decodeID(self.format, id)
                        book.id = id
                        self.books.append(book)

#           setTitles()
#           titles = getTitles()
#           firstVerse = Verse(book: minBook, chapter: 1, number: 1, count: 1)
#           books.sort(by: {$0.sorting < $1.sorting} )

            self.loaded = True
        except:
            print("loadDatabase exception")
            return

    def getChapter(self, verse: Verse) -> [str]:
        id = Module.encodeID(self.format, verse.book)
        nt = isNewTestament(verse.book)
        z = self.z
        query = f"SELECT * FROM {z.bible} WHERE {z.book}={id} AND {z.chapter}={verse.chapter}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                text = row.get(z.text.capitalize(), "")
#               text = preparation(text, format: format, nt: nt, purge: false)
                result.append(text)
            return result
        except:
            print("exception2")
            return []

path = "bibles/rstw.unbound"
path = "bibles/AMP.SQLite3"
bible = Bible(path)

verse = Verse()
verse.book    = 40
verse.chapter = 2
verse.number  = 1
verse.count   = 0

out = bible.loadDatabase()
#out = bible.getChapter(verse)
print()
#for s in out: print(s)
