#
#  module.py
#  Unbound Bible Python Edition
#

import os
import glob
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

#       self.rightToLeft = getRightToLeft(self.language)
        self.connected = True
#       print(self.info)

class Bible(Module):

    class _Book:
        title   = ""
        abbr    = ""
        number  = 0
        sorting = 0

    def __init__(self, atPath: str):
        super().__init__(atPath)
        self._books = []
        self.loadDatabase() # temp

    def loadDatabase(self):
        if self.loaded: return
        query = "SELECT * FROM Books"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except:
            print("loadDatabase exception")
            return

        for row in rows:
            number = row.get("Number", 0)
            if number > 0:
                book = self._Book()
                book.number = number
                book.title = row.get("Name", "")
                book.abbr = row.get("Abbreviation", "")
                self._books.append(book)
                self.loaded = True

#       firstVerse = Verse(book: minBook, chapter: 1, number: 1, count: 1)

    def bookByName(self, name: str) -> int:
        for book in self._books:
            if book.title == name:
                return book.number
        return None

    def getTitles(self) -> [str]:
        result = []
        for book in self._books:
            result.append(book.title)
        return result

    def chaptersCount(self, verse: Verse) -> int:
        query = f"SELECT MAX(Chapter) AS Count FROM Bible WHERE Book = {verse.number}";

        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            count = row.get("Count", 0)
            return count
        except:
            print("chaptersCount exception")
            return 0

    def getChapter(self, verse: Verse) -> [str]:
        nt = isNewTestament(verse.book)
        query = f"SELECT * FROM Bible WHERE Book={verse.book} AND Chapter={verse.chapter}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                text = row.get("Scripture", "")
#               text = preparation(text, nt, purge: false)
                result.append(text)
            return result
        except:
            print("getChapter exception")
            return []

class Shelf():
    current = 3

    def __init__(self):
        self.bibles = []
        self._load()
#       bibles.sort(by: {$0.name < $1.name} )

    def _load(self):
        files = glob.glob("bibles/*.unbound")

        for file in files:
            print(file)
            item = Bible(file)
            self.bibles.append(item)

    def setCurrent(self, index: int):
        if index >= len(self.bibles): return
        self.current = index
        print(self.current)
        self.bibles[self.current].loadDatabase()

#       if not self.bibles[self.current].goodLink(activeVerse):
#           activeVerse = bibles[current].firstVerse

    def isEmpty(self) -> bool:
        return False if self.bibles else True

currVerse = Verse()
currVerse.book    = 40
currVerse.chapter = 2
currVerse.number  = 1
currVerse.count   = 0

shelf = Shelf()

def currBible():
    return shelf.bibles[shelf.current]
