import sqlite3

con = None
con = sqlite3.connect("/home/pieterse/Compile/nut_tcltk/nut.sqlite")

cur = con.cursor()

cur.execute('SELECT NDB_No,Long_Desc FROM food_des WHERE NDB_No>30060')

while True:
    data = cur.fetchone()

    if data == None: break
    print "Data: ", data



import sys
try:
   import pygtk
   pygtk.require("2.0")
except:
   pass
try:
   import gtk
   import gtk.glade
except:
   sys.exit(1)



class Handler:
   def onDeleteWindow(self, *args):
      gtk.main_quit(*args)

   def mySearch(self, entry):
      print "Entry contains: ", entry.get_text()

      print t.get_cursor()
      print t.get_cursor().get_title()


builder = gtk.Builder()
builder.add_from_file("nut.glade")
builder.connect_signals(Handler())

t = builder.get_object("treeview1")

liststore = gtk.ListStore(str)

liststore.append(["1"])
liststore.append(["HUBBLe"])
liststore.append(["MARS1"])
liststore.append(["MARS2"])
liststore.append(["MARS3"])
liststore.append(["MARS4"])
liststore.append(["MARS5"])
liststore.append(["MARS6"])
liststore.append(["MARS7"])
liststore.append(["MARS8"])
liststore.append(["MARS9 maar dan een hele lang die eigenlijk niet op het scherm past, maar nu nog wel omdat de window scaled..."])
liststore.append(["MARS9"])
liststore.append(["MARS0"])
liststore.append(["m5"])
for i in range(10):
    liststore.append(["planet%d"%(i)])
        
t.set_model(liststore)
column = gtk.TreeViewColumn("Matched foods:")
t.append_column(column)
        
cell = gtk.CellRendererText()
column.pack_start(cell, False)
column.add_attribute(cell, "text", 0)

window = builder.get_object("window1")
window.show_all()
gtk.main()
