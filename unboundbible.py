"""

Unbound Bible Python Edition
Open Source Application

"""

import os
import re
import configparser

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
from bible import *

# Window

win = Tk()
win.withdraw()
win.title("Unbound Bible PE")
if os.name == 'nt': win.iconbitmap('icons/unboundbible.ico')

def popup(event):
    cmenu.tk_popup(event.x_win, event.y_win, 0)

def theme(event=None):
    global bgc,fgc
    val = themechoice.get()
    clrs = clrschms.get(val)
    fgc, bgc = clrs.split('.')
    fgc, bgc = '#'+fgc, '#'+bgc
    bookBox.config(bg=bgc, fg=fgc)
    chapterBox.config(bg=bgc, fg=fgc)
    memo.config(bg=bgc, fg=fgc)

#   combostyle = ttk.Style()
#   settings = {'TCombobox':{'configure':{'selectbackground': 'red','fieldbackground': 'blue','background': 'green'}}}
#   combostyle.theme_create('combostyle', parent='alt', settings = settings)
#   combostyle.theme_use('combostyle')

#######################################################################

def about(event=None):
    messagebox.showinfo("About","Unbound Bible Python Edition \n\n Open Source Application")

def help_box(event=None):
    pass

#######################################################################

def select_all(event=None):
        memo.tag_add('sel', '1.0', 'end')
        return

def on_find():
    entry.focus_set()

def copy(event=None):
    memo.event_generate("<<Copy>>")

def compare(event=None):
    print('compare')
    pass

def on_exit(event=None):
    saveConfig()
    win.destroy()

######################################################################

copyicon = PhotoImage(file='icons/copy.gif')
compricon = PhotoImage(file='icons/compare.gif')

menubar   = Menu(win)

toolsmenu = Menu(menubar, tearoff=0 )
toolsmenu.add_command(label="Find",underline= 0, accelerator='Ctrl+F', command=on_find)

themesmenu = Menu(menubar, tearoff=0)
toolsmenu.add_cascade(label="Themes", menu=themesmenu)

clrschms = {
'1. Default White': '000000.FFFFFF',
'2. Greygarious Grey':'83406A.D1D4D1',
'3. Lovely Lavender':'202B4B.E1E1FF' ,
'4. Aquamarine': '5B8340.D1E7E0',
'5. Bold Beige': '4B4620.FFF0E1',
'6. Cobalt Blue':'ffffBB.3333aa',
'7. Olive Green': 'D1E7E0.5B8340',
}

themechoice= StringVar()
themechoice.set('1. Default White')
for k in sorted(clrschms):
    themesmenu.add_radiobutton(label=k, variable=themechoice, command=theme)

menubar.add_cascade(label="Tools", menu=toolsmenu)
toolsmenu.add_separator()
toolsmenu.add_command(label="Exit", accelerator='Alt+F4', command=on_exit)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Copy", compound=LEFT, image=copyicon,  accelerator='Ctrl+C', command=copy)
editmenu.add_command(label="Select All", underline=7, accelerator='Ctrl+A', command=select_all)
menubar.add_cascade(label="Edit", menu=editmenu)

aboutmenu = Menu(menubar, tearoff=0)
aboutmenu.add_command(label="About", command=about)
aboutmenu.add_cascade(label="Help", command=help_box)
menubar.add_cascade(label="About",  menu=aboutmenu)

win.config(menu=menubar) # Returning defined setting for widget

# Shortcut Icon Toolbar

shortcutbar = Frame(win,  height=25)

icons = ['copy', 'compare', 'on_find', 'about']
for i, icon in enumerate(icons):
    tbicon = PhotoImage(file=f'icons/{icon}.gif')
    cmd = eval(icon)
    toolbar = Button(shortcutbar, image=tbicon, command=cmd)
    toolbar.image = tbicon
    toolbar.pack(side=LEFT)

# Separator

separator = Label(shortcutbar, text='')
separator.pack(side=RIGHT)

# Entry

def return_entry(event=None):
    text = entry.get()
    loadSearch(text)

entryVar = StringVar()
entry = Entry(shortcutbar, width=25, textvariable=entryVar)
entry.bind('<Return>', return_entry)
entry.pack(side=RIGHT)

shortcutbar.pack(expand=NO, fill=X)

# Status Bar

status = Label(win, text="")
status.pack(expand=NO, fill=X, side=BOTTOM, anchor='se')

# Text & ScrollBar

def memoLoad(text: str):
    memo.delete(1.0, END)
    memo.insert(1.0, text)

memo = Text(win, wrap=WORD, undo=True)
memo.pack(side=RIGHT, expand=YES, fill=BOTH)

scroll=Scrollbar(memo)
memo.configure(yscrollcommand=scroll.set)
scroll.config(command=memo.yview)
scroll.pack(side=RIGHT, fill=Y)

# Combobox

def comboboxSelect(event=None):
    if event: # this works only with bind because `command=` doesn't send event
        index = combobox.current()
        shelf.setCurrent(index)
        makeBookList()
        goToVerse(currVerse)
        status['text'] = " " + currBible().fileName + " | " + currBible().info

combolist = []
for bible in shelf.bibles:
    combolist.append(" " + bible.name)
combobox = Combobox(win, textvariable = StringVar(), values=combolist)
combobox.bind("<<ComboboxSelected>>", comboboxSelect)
combobox.pack(side=TOP, fill=X)

# BookBox

def makeBookList():
    bookBox.delete(0,END)
    for title in currBible().getTitles():
        bookBox.insert(END, " " + title)

def bookBoxSelect(event=None):
    if event:
        curselection = bookBox.curselection()
        if curselection:
            selection = curselection[0]
            titles = currBible().getTitles()
            sbook = titles[selection]
            book = currBible().bookByName(sbook).number
            if book:
                currVerse.reset()
                currVerse.book = book
                loadChapter()

bookBox = Listbox(win, height=4)
bookBox.bind("<<ListboxSelect>>", bookBoxSelect)
bookBox.pack(side=LEFT, fill=BOTH)

# ChapterBox

def makeChapterList():
    chapterBox.delete(0,END)
    max = currBible().chaptersCount(currVerse)
    for n in range(1, max + 1):
        chapterBox.insert(END, " " + str(n))
#   if ChapterBox.Items.Count = n then Exit;

def chapterBoxSelect(event=None):
    if event:
        selection = chapterBox.curselection()
        if selection:
            chapter = selection[0] + 1
            currVerse.chapter = chapter;
            currVerse.number = 1;
            currVerse.count = 1;
            loadChapter()

chapterBox = Listbox(win, height=4)
chapterBox.bind("<<ListboxSelect>>", chapterBoxSelect)
chapterBox.pack(side=LEFT, fill=BOTH)

# Popup Menu

cmenu = Menu(memo)
cmd = eval('copy')
cmenu.add_command(label=i, compound=LEFT, command=cmd)
cmenu.add_separator()
cmenu.add_command(label='Select All', underline=7, command=select_all)
memo.bind("<Button-3>", popup)

# Events

memo.bind('<Control-A>', select_all)
memo.bind('<Control-a>', select_all)
memo.bind('<Control-f>', on_find)
memo.bind('<Control-F>', on_find)
memo.bind('<KeyPress-F1>', help_box)

memo.tag_configure("active_line", background="ivory2")

def goToVerse(verse: Verse):
    if not currBible().goodLink(verse): return
    currVerse = verse
    loadChapter()

def applyTags(s: str) -> str:
    s = re.sub( '<S>',' ', s)
    s = re.sub( '<i>','[', s)
    s = re.sub('</i>',']', s)
    s = re.sub(r'<.*?>','',s)
    return s

def loadChapter():
    strings = currBible().getChapter(currVerse)
    text = ""
    for i in range(len(strings)):
        s = applyTags(strings[i])
        text += f" {i+1} {s}\n"
    memoLoad(text)
    makeChapterList()

def loadSearch(target: str):
    if len(target) < 3:  return
    strings = currBible().getSearch(target)
    text = ""
    for s in strings:
        s = applyTags(s)
        text += f"{s}\n\n"
    if not strings:
        text = f"You search for '{target}' produced no results."
    memoLoad(text)
    memo.focus_set()
    status['text'] = f" {len(strings)} verses found."

# Config

def saveConfig():
    config = configparser.ConfigParser()
    config.read("config.ini", "utf8")

    if "Application" not in config.sections():
        config.add_section("Application")

    config.set('Application','filename', currBible().fileName)

    config.set('Application','left', f'{win.winfo_x()}')
    config.set('Application','top',  f'{win.winfo_y()}')
    config.set('Application','width',  f'{win.winfo_width()}')
    config.set('Application','height', f'{win.winfo_height()}')

    f = open('config.ini', 'w', encoding='utf8')
    config.write(f)
    f.close()

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini", "utf8")

    try:
        fileName = config.get('Application','filename')
        shelf.setCurrentByName(fileName)
        combobox.current(shelf.current)

        left = config.get('Application', 'left')
        top  = config.get('Application', 'top')
        width  = config.get('Application', 'width')
        height = config.get('Application', 'height')

        win.geometry(f'{width}x{height}+{left}+{top}')
    except:
        combobox.current(0)
        win.geometry('640x480')

# Init

readConfig()
makeBookList()
loadChapter()
status['text'] = " " + currBible().fileName + " | " + currBible().info

win.protocol("WM_DELETE_WINDOW", on_exit)
win.deiconify()
win.mainloop()
