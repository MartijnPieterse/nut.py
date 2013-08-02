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

sql = "SELECT Tagname,Units FROM nutr_def"
cur.execute(sql)

all_food_nutr = []
while True:
    data = cur.fetchone()

    if data == None: break
    all_food_nutr.append((data[0], data[1]))

def sqlGetNutrName(id):
    sql = "SELECT NutrDesc FROM nutr_def WHERE Nutr_No=" + repr(id)
    cur.execute(sql)
    data = cur.fetchone()

    if data == None: return "None"
    return data[0]

def sqlGetNutrTagName(id):
    sql = "SELECT Tagname FROM nutr_def WHERE Nutr_No=" + repr(id)
    cur.execute(sql)
    data = cur.fetchone()

    if data == None: return "None"
    return data[0]

def sqlGetNutrUnit(id):
    sql = "SELECT Units FROM nutr_def WHERE Nutr_No=" + repr(id)
    cur.execute(sql)
    data = cur.fetchone()

    if data == None: return "--"
    return data[0]

# Layout should move into the database, probably.
# For now:
# None = Empty
# Negative values are special.
# -1 = Prot/Carb/Fat
# -2 = Omega 6/3 Balance
layout = [ [  208,  205,  203 ],
           [   -1,  291, 2000 ],
           [ None, None, None ],
           [  204,  401,  301 ],
           [  606,  404,  312 ],
           [  645,  405,  303 ],
           [  646,  406,  304 ],
           [ 2006,  410,  315 ],
           [ 2001,  415,  305 ],
           [ 2002,  431,  306 ],
           [ 2007,  418,  317 ],
           [ 2003,  318,  307 ],
           [ 2004,  324,  309 ],
           [ 2005, 2008, None ],
           [  601,  430,   -2 ] ]


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

        self.createNutritionTabs(builder.get_object("table1"))
        ### Make all connections
    
        # Connect search entry
        builder.get_object("entry_vft_search").connect("changed", self.entry_vft_search_changed_cb)

        # Connect search results to update nutrients when chosen
        self.sel_search_results.connect("changed", self.onFoodChanged)

    def createNutritionTabs(self, table):
        # First Set Size!
        table.resize(len(layout[0])*3, len(layout))

        self.crossref = { }
        # Add dummy labels to every unit
        for i in xrange(len(layout)):
            for j in xrange(len(layout[i])):
                l = layout[i][j]

                label1 = gtk.Label()
                label2 = gtk.Label()
                label3 = gtk.Label()

                top = i
                bottom = i+1

                if l == None:
                    pass
                elif l < 0:
                    label1.set_text("***Special***")
                else:
                    label1.set_text(sqlGetNutrName(l))
                    label2.set_alignment(1.0, 0.5)
                    label3.set_text(" "+sqlGetNutrUnit(l))
                    label3.set_alignment(0.0, 0.5)

                    self.crossref[l] = label2

                left = j*3
                right = j*3+1
                table.attach(label1, left, right, top, bottom)
                table.attach(label2, left+1, right+1, top, bottom)
                table.attach(label3, left+2, right+2, top, bottom)


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
        
        assert len(pathlist) <= 1
        for path in pathlist :
            tree_iter = model.get_iter(path)
            value0 = model.get_value(tree_iter,0)
            value1 = model.get_value(tree_iter,1)

            # Create SQL
            sql = "SELECT "

            for i in layout:
                for j in i:
                    if j != None and j >= 0: sql += sqlGetNutrTagName(j) + ",";

            sql = sql.rstrip(",") + " FROM food_des WHERE NDB_No=%s" % (value0)

            #print sql

            cur.execute(sql)
            
            data = cur.fetchone()

            data_index = 0
            for i in layout:
                for j in i:
                    if j != None and j>=0:
                        if data[data_index] != None:

                            t = float(data[data_index])

                            t = ("%.3f" % (t)).rstrip("0").rstrip(".")

                            self.crossref[j].set_text(t)
                            #print j, t, len(t)
                        else:
                            self.crossref[j].set_text("(nd)")
                        data_index += 1
            # TODO Some sort of redraw??
                          



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class nutWindowHandlers:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Catch all handlers defined via glade.
#
    def windowNutMain_delete_event_cb(self, *args):
        gtk.main_quit(args)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class testTab:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Test if Nutrient Tabs Generator can work
#
    def __init__(self, builder):

        table = builder.get_object("testTable")

        # First Set Size!
        table.resize(len(layout[0]), len(layout))

        # Add dummy labels to every unit
        for i in xrange(len(layout)):
            for j in xrange(len(layout[i])):
                l = layout[i][j]

                label1 = gtk.Label()
                label2 = gtk.Label()

                top = i
                bottom = i+1

                if l == None:
                    pass
                elif l < 0:
                    label1.set_text("***Special***")
                else:
                    label1.set_text(sqlGetNutrName(l))

                left = j*2
                right = j*2+1
                table.attach(label1, left, right, top, bottom)
                table.attach(label2, left+1, right+1, top, bottom)


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

    yyy = testTab(builder)

    # Show off
    window = builder.get_object("windowNutMain")
    window.show_all()
    gtk.main()



nutMain()
