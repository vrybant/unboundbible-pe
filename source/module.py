#
#  module.py
#  Unbound Bible Python Edition
#

import sqlite3
from data import *

def dict_factory(cursor, row) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Module:
    database     = None
    cursor       = None
    filePath     = ""
    fileName     = ""

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
        self.openDatabase()

    def tableExists(cursor, tablename) -> bool:
        query = f"PRAGMA table_info({tablename})" # case insensitive method
        cursor.execute(query)
        return cursor.fetchone() != None

    def openDatabase(self):
        try:
            self.database = sqlite3.connect(self.filePath)
            self.database.row_factory = dict_factory
            self.cursor = self.database.cursor()
        except:
            print("connect database exception")
            return

        query = "select * from Details"
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
        except:
            print("open database exception")
            return

        self.info      = row.get("Information",  "")
        self.info      = row.get("Description", self.info)
        self.name      = row.get("Title",       self.info)
        self.abbr      = row.get("Abbreviation", "")
        self.copyright = row.get("Copyright",    "")
        self.language  = row.get("Language",     "")
        self.strong    = row.get("Strong",       "")
        self.embedded  = row.get("Embedded",     "")

#       self.rightToLeft = getRightToLeft(self.language)
        self.connected = True
        print(self.info)

class Bible(Module):
    books = [Book()]
    titles = [str]

    def __init__(self, atPath: str):
        super().__init__(atPath)

#        embtitles = database!.tableExists(z.titles)
#        if connected && !database!.tableExists(z.bible) { return nil }

    def loadDatabase(self):
        if self.loaded: return
        query = "SELECT DISTINCT Book FROM Bible"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            for row in rows:
                value = row.get("Book", 0)
                if type(value) is int:
                    if value > 0:
                        book = Book()
                        book.number = value
                        self.books.append(book)

#           setTitles()
#           titles = getTitles()
#           firstVerse = Verse(book: minBook, chapter: 1, number: 1, count: 1)
#           books.sort(by: {$0.sorting < $1.sorting} )

            self.loaded = True
        except:
            print("loadDatabase exception")
            return

        def getTitles() -> [Title()]:
            query = "SELECT * FROM Titles"
            try:
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
            except:
                print("ExternalTitles getData() exception")
                return []

#           result = [Title]()
            result = []
            k = 0
            for row in rows:
                t = Title()
                t.number = row.get("Number", 0)
                t.name = row.get("Name", "")
                t.abbr = row.get("Abbreviation", "")
                if not isNewTestament(t.number): t.sorting = k + 100
                result.append(t)
                k += 1

            return result

    def getChapter(self, verse: Verse) -> [str]:
        nt = isNewTestament(verse.book)
        query = f"SELECT * FROM Bible WHERE Book={verse.book} AND Chapter={verse.chapter}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                text = row.get("Scripture", "")
#               text = preparation(text, format: format, nt: nt, purge: false)
                result.append(text)
            return result
        except:
            print("exception2")
            return []

path = "bibles/rstw.unbound"
bible = Bible(path)

verse = Verse()
verse.book    = 40
verse.chapter = 2
verse.number  = 1
verse.count   = 0

out = bible.loadDatabase()
out = bible.getChapter(verse)
print()
for s in out: print(s)
