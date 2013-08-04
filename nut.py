#!/bin/env python
#

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

def sqlGetWeightFor(id):
    sql = "SELECT Msre_Desc,Amount,whectograms FROM weight WHERE NDB_No=" + repr(id) + " ORDER BY Seq"

    cur.execute(sql)
    data = cur.fetchone()

    result = []

    while data != None:
        result.append([data[0], data[1], data[2]])

        data = cur.fetchone()

    return result

# Layout should move into the database, probably.
# For now:
# None = Empty
# Negative values are special.
# -1 = Prot/Carb/Fat
# -2 = Omega 6/3 Balance
layout = { "nutrients": [ [  208,  205,  203 ],
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
                          [  601,  430,   -2 ]
                        ],
           "carbsamino": [ [ None, None, None ],
                           [ None, None, None ],
                           [  205,  203,  504 ],
                           [  291,  257,  505 ],
                           [  209,  513,  506 ],
                           [  269,  511,  508 ],
                           [  212,  514,  517 ],
                           [  287,  507,  518 ],
                           [  211,  515,  502 ],
                           [  213,  516,  501 ],
                           [  214,  512,  509 ],
                           [  210,  521,  510 ],
                           [ None,  503, None ],
                           [ None, None, None ],
                           [ None, None, None ]
                         ],
           "miscellaneous": [ [ None, None, None ],
                              [  268,  319,  343 ],
                              [  207,  320,  322 ],
                              [  255,  325,  321 ],
                              [  262,  326,  334 ],
                              [  263,  328,  338 ],
                              [  221,  578,  337 ],
                              [  313,  573,  601 ],
                              [  454,  429,  636 ],
                              [  421,  428,  641 ],
                              [  431,  323,  639 ],
                              [  432,  341,  638 ],
                              [  435,  342, None ],
                              [ None, None, None ],
                              [ None, None, None ]
                            ],
           "fat1" : [ [  606, None ],
                      [  607,  645 ],
                      [  608,  625 ],
                      [  609,  697 ],
                      [  610,  626 ],
                      [  611,  673 ],
                      [  696,  687 ],
                      [  612,  617 ],
                      [  652,  674 ],
                      [  613,  628 ],
                      [  653,  630 ],
                      [  614,  676 ],
                      [  615,  671 ],
                      [  624, None ],
                      [  654, None ]
                    ],
           "fat2" : [ [ None, None, None ],
                      [ None, None,  605 ],
                      [ None,  689,  693 ],
                      [  646,  852,  662 ],
                      [  618,  853,  663 ],
                      [  672,  620,  859 ],
                      [  619,  855,  664 ],
                      [  851,  629,  695 ],
                      [  685,  857,  666 ],
                      [  627,  858,  665 ],
                      [  672,  631,  669 ],
                      [ None,  621,  670 ],
                      [ None, None,  856 ],
                      [ None, None, None ],
                      [ None, None, None ]
                    ]
         }


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
        self.ls_combobox = gtk.ListStore(str, float, float)

        self.combobox.set_model(self.ls_combobox)
        cell = gtk.CellRendererText()
        self.combobox.pack_start(cell, True)
        self.combobox.add_attribute(cell, 'text', 0)
        self.combobox.set_active(0)
        self.combobox.connect("changed", self.combobox_changed_cb)

        builder.get_object("vf_spinb_amount").connect("changed", self.onSpinB_cb)


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

        self.createNutritionTabs()
        ### Make all connections
    
        # Connect search entry
        builder.get_object("entry_vft_search").connect("changed", self.entry_vft_search_changed_cb)

        # Connect search results to update nutrients when chosen
        self.sel_search_results.connect("changed", self.onFoodChanged)

        

    def createNutritionTabs(self):

        self.crossref = { }
        for k in layout.keys():
            table = self.builder.get_object("vf_notebook_table_"+k)
            # First Set Size!
            table.resize(len(layout[k][0])*3, len(layout[k]))

            # Add dummy labels to every unit
            for i in xrange(len(layout[k])):
                for j in xrange(len(layout[k][i])):
                    l = layout[k][i][j]

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

                        self.crossref[k+repr(l)] = label2

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
            
            # Update combobox

            self.ls_combobox.clear()
            w = sqlGetWeightFor(value0)
            for i in w:
                self.ls_combobox.append([i[0], i[1], i[2]])
            self.combobox.set_active(0)
            self.builder.get_object("vf_spinb_amount").set_value(float(w[0][1]))

            # Set multiplier
            multiplier = float(w[0][2])

            self.updateAllNutrients(value0, multiplier)


        self.builder.get_object("windowNutMain").queue_draw()

    def updateAllNutrients(self, nut_id, multiplier):
        for k in layout.keys():
            # Create SQL
            sql = "SELECT "

            for i in layout[k]:
                for j in i:
                    if j != None and j >= 0: sql += sqlGetNutrTagName(j) + ",";

            sql = sql.rstrip(",") + " FROM food_des WHERE NDB_No=%s" % (nut_id)

            #print sql

            cur.execute(sql)
            
            data = cur.fetchone()

            data_index = 0
            for i in layout[k]:
                for j in i:
                    if j != None and j>=0:
                        self.crossref[k+repr(j)].set_text("")
                        if data[data_index] != None:

                            t = float(data[data_index]) * multiplier

                            t = ("%.3f" % (t)).rstrip("0").rstrip(".")

                            self.crossref[k+repr(j)].set_text(t)
                            #print j, t, len(t)
                        else:
                            self.crossref[k+repr(j)].set_text("(nd)")
                        data_index += 1
            # TODO Some sort of redraw??
            #??self.builder.get_object("table1").queue_draw()



    def combobox_changed_cb(self, e):
        a = self.combobox.get_active()

        if a != -1:
            i = self.ls_combobox.get_iter_first()

            for dummy in xrange(a): i = self.ls_combobox.iter_next(i)

            self.builder.get_object("vf_spinb_amount").set_value(self.ls_combobox.get_value(i, 1))

            if i != None:
                multiplier = self.ls_combobox.get_value(i, 2)

                (model, pathlist) = self.sel_search_results.get_selected_rows()
                
                assert len(pathlist) <= 1
                for path in pathlist :
                    tree_iter = model.get_iter(path)
                    value0 = model.get_value(tree_iter,0)

                self.updateAllNutrients(value0, multiplier)


    def onSpinB_cb(self, e):
        spv = float( self.builder.get_object("vf_spinb_amount").get_value() )
        a = self.combobox.get_active()

        if a != -1:
            i = self.ls_combobox.get_iter_first()

            for dummy in xrange(a): i = self.ls_combobox.iter_next(i)

            if i != None:
                multiplier = self.ls_combobox.get_value(i, 2)

                spv = spv / float(self.ls_combobox.get_value(i, 1))

                (model, pathlist) = self.sel_search_results.get_selected_rows()
                
                assert len(pathlist) <= 1
                for path in pathlist :
                    tree_iter = model.get_iter(path)
                    value0 = model.get_value(tree_iter,0)

                self.updateAllNutrients(value0, multiplier*spv)


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

#    yyy = testTab(builder)

    # Show off
    window = builder.get_object("windowNutMain")
    window.show_all()
    gtk.main()



nutMain()
