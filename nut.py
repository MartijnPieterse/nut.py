import sqlite3

con = None
con = sqlite3.connect("/home/pieterse/Compile/nut_tcltk/nut.sqlite")

cur = con.cursor()

cur.execute('SELECT NDB_No,Long_Desc FROM food_des WHERE Long_Desc LIKE "%kol%"');

while True:
    data = cur.fetchone()

    if data == None: break
    print "Data: [", data, "]", data[0], data[1]


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
        e = entry.get_text()
        print "Entry contains: ", e
        liststore.clear()
        
        if len(e) >= 3:
            sql = "SELECT NDB_No,Long_Desc FROM food_des WHERE Long_Desc LIKE \"%" + entry.get_text() + "%\""

            print sql
            cur.execute(sql)

            while True:
                data = cur.fetchone()

                if data == None: break
                liststore.append([data[0], data[1]])
                

def onSelectionChanged(a):
    print a

    (model, pathlist) = tree_selection.get_selected_rows()
    for path in pathlist :
        print "a"
        tree_iter = model.get_iter(path)
        value0 = model.get_value(tree_iter,0)
        print value0
        value1 = model.get_value(tree_iter,1)
        print value1       

        sql = "SELECT CHOCDF FROM food_des WHERE NDB_No=%s" % (value0)
        cur.execute(sql)
        
        data = cur.fetchone()

        value = data[0]
        e = builder.get_object("CHOCDF")
        print e

        e.set_text(repr(value))


builder = gtk.Builder()
builder.add_from_file("nut.glade")
builder.connect_signals(Handler())

t = builder.get_object("treeview1")

liststore = gtk.ListStore(int, str)

t.set_model(liststore)
column1 = gtk.TreeViewColumn("Hidden:")
t.append_column(column1)
column2 = gtk.TreeViewColumn("Matched foods:")
t.append_column(column2)

cell = gtk.CellRendererText()

column1.pack_start(cell, False)
column1.add_attribute(cell, "text", 0)
column2.pack_start(cell, False)
column2.add_attribute(cell, "text", 1)

tree_selection = t.get_selection()      
tree_selection.connect("changed", onSelectionChanged)

window = builder.get_object("window1")
window.show_all()
gtk.main()
