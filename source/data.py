#
#  data.py
#  Unbound Bible Python Edition
#

class Verse:
    book    = 0
    chapter = 0
    number  = 0
    count   = 0

class minVerse:
    book    = 1
    chapter = 1
    number  = 1
    count   = 1

class Title:
    name    = ""
    abbr    = ""
    number  = 0
    sorting = 0

class Verse:
    book    = 0
    chapter = 0
    number  = 0
    count   = 0

class Book:
    title   = ""
    abbr    = ""
    number  = 0
    sorting = 0

class unboundAlias:
    bible   = "Bible"
    book    = "Book"
    chapter = "Chapter"
    verse   = "Verse"
    text    = "Scripture"
    titles  = "Titles"
    number  = "Number"
    name    = "Name"
    abbr    = "Abbr"

def isNewTestament(n: int) -> bool:
     return n >= 40 and n < 77


