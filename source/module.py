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
    _books = []

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
        except:
            print("loadDatabase exception")
            return

        for row in rows:
            value = row.get("Book", 0)
            if type(value) is int:
                if value > 0:
                    book = Book()
                    book.number = value
                    self._books.append(book)

        self.setTitles()
        for b in self._books: print(b.number, b.title)

#       firstVerse = Verse(book: minBook, chapter: 1, number: 1, count: 1)
#       books.sort(by: {$0.sorting < $1.sorting} )

        self.loaded = True

    def setTitles(self):
        try:
            query = "SELECT * FROM Titles"
            self.cursor.execute(query)
            titles = self.cursor.fetchall()
        except:
            print("setTitles exception")
            return

        for book in self._books:
            unknown = "Unknown " + str(book.number)
            k = 0
            for row in titles:
                number = row.get("Number", 0)
                if number == book.number:
                    book.title = row.get("Name", unknown)
                    book.abbr = row.get("Abbreviation", "")
                    book.sorting = k
                    if not isNewTestament(book.number): book.sorting = k + 100
                    k += 1

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
            print("getChapter exception")
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
