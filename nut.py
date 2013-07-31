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

   def onButton1Pressed(self, button):
      print "Hello World!"

   def onButton2Pressed(self, button):
      print "Destroy The World!"

   def menu_quit_action(self, menu):
      print "menu Quit"
      gtk.main_quit()
      
   def mySearch(self, entry):
      print "x"
      t = builder.get_object("treeview2")

      l = gtk.ListStore(str)

      l.append(["MAPI"])
      t.set_model(l)
   
builder = gtk.Builder()
builder.add_from_file("nut.glade")
builder.connect_signals(Handler())

t = builder.get_object("treeview2")

liststore = gtk.ListStore(str)
        
liststore.append(["Ubuntu"])
liststore.append(["Fedora"])
liststore.append(["Sabayon"])
liststore.append(["Arch"])
liststore.append(["Debian"])
        
t.set_model(liststore)
column = gtk.TreeViewColumn("Selected.. No.. found..")
t.append_column(column)
        
cell = gtk.CellRendererText()
column.pack_start(cell, False)
column.add_attribute(cell, "text", 0)


window = builder.get_object("window1")
window.show_all()
gtk.main()
