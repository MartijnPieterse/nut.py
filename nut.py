#!/bin/env python
import sqlite3
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




con = None
con = sqlite3.connect("/home/pieterse/Compile/nut_tcltk/nut.sqlite")
cur = con.cursor()

sql = "SELECT Tagname FROM nutr_def"
cur.execute(sql)

all_food_nutr = []
while True:
    data = cur.fetchone()

    if data == None: break
    all_food_nutr.append(data[0])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class viewfoodTab:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Handles the whole "View Foods" tab.
#   Arrange all nutrients when in the View Foods tab.
#

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, builder):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Initialize.
    # Input:
    #   SQL reference
    #   Nutrients widget

        # TODO Temporary
        self.builder = builder

        ### Setup widgets that cannot be done in Glade for some reason.

        # Setup the combobox for the serving size
        self.combobox = builder.get_object("combobox_vft_servingsize")
        ls_combobox = gtk.ListStore(str)
        ls_combobox.append(["g"])
        ls_combobox.append(["oz"])
        ls_combobox.append(["servings"])

        self.combobox.set_model(ls_combobox)
        cell = gtk.CellRendererText()
        self.combobox.pack_start(cell, True)
        self.combobox.add_attribute(cell, 'text', 0)
        self.combobox.set_active(0)

        # Setup the search results

        self.ls_search_results = gtk.ListStore(int, str)

        t = builder.get_object("treeview_vft_searchresult")
        t.set_model(self.ls_search_results)

        column = gtk.TreeViewColumn("Matched foods:")
        t.append_column(column)

        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, "text", 1)

        self.sel_search_results = t.get_selection()

        ### Make all connections
    
        # Connect search entry
        builder.get_object("entry_vft_search").connect("changed", self.entry_vft_search_changed_cb)

        # Connect search results to update nutrients when chosen
        self.sel_search_results.connect("changed", self.onFoodChanged)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def entry_vft_search_changed_cb(self, entry):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   If the entered text is >=3 query the database for the foods.
        
        # Clear list
        self.ls_search_results.clear()

        e = entry.get_text()

        
        if len(e) >= 3:
            sql = "SELECT NDB_No,Long_Desc FROM food_des WHERE Long_Desc LIKE \"%" + entry.get_text() + "%\""
            cur.execute(sql)

            while True:
                data = cur.fetchone()

                if data == None: break
                self.ls_search_results.append([data[0], data[1]])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def onFoodChanged(self, food_id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Upon selecting, or changing the selection of a food, read all
    #   nutrients from the database and update them on the UI
    # Input:
    #   food_id -  - food must be available in the database.
    #
        (model, pathlist) = self.sel_search_results.get_selected_rows()
        
        assert len(pathlist) == 1
        for path in pathlist :
            tree_iter = model.get_iter(path)
            value0 = model.get_value(tree_iter,0)
            value1 = model.get_value(tree_iter,1)

            # Create SQL
            sql = "SELECT "
            for n in all_food_nutr:
                sql += n + ","
            sql = sql.rstrip(",") + " FROM food_des WHERE NDB_No=%s" % (value0)

            cur.execute(sql)
            
            data = cur.fetchone()

            for n,d in zip(all_food_nutr, data):
                e = self.builder.get_object("vf_nut_"+n)

                if e != None:
                    if d != None: e.set_text(repr(d))
                    else: e.set_text("(nd)")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class nutWindowHandlers:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Catch all handlers defined via glade.
#
    def windowNutMain_delete_event_cb(self, *args):
        gtk.main_quit(args)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def nutMain():
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   BLA
#   bla
#   bla
#
    builder = gtk.Builder()
    builder.add_from_file("nut.glade")

    builder.connect_signals(nutWindowHandlers())



    xxx = viewfoodTab(builder)

    # Show off
    window = builder.get_object("windowNutMain")
    window.show_all()
    gtk.main()



nutMain()
