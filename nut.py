#!/bin/env python
# -*- coding: iso-8859-15 -*-
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


import gobject
import datetime




# TODO Make "data" class. Which is to be used to retrieve all data.
#      Data can then reside in database or text file, or whatever.

con = None
con = sqlite3.connect("nut.sqlite")
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

def sqlGetFoodNutrientValue(food_id, field_ids):
    sql = "SELECT "

    for field in field_ids:
        sql += sqlGetNutrTagName(field) + ","

    sql = sql.rstrip(",") + " FROM food_des WHERE NDB_No=%s" % (food_id)

    cur.execute(sql)
    data = cur.fetchone()

    # Should be only one!

    result = {}

    for n in zip(field_ids,data):
        result[n[0]] = n[1]

    return result

def sqlGetFoodNutrientValues(food_ids, field_ids):
    sql = "SELECT "

    for field in field_ids:
        sql += sqlGetNutrTagName(field) + ","

    sql = sql.rstrip(",") + " FROM food_des WHERE NDB_No IN ("

    for fi in food_ids:
        sql += "%s," % (fi)

    sql = sql.rstrip(",") + ")"

    cur.execute(sql)
    data = cur.fetchone()

    # Should be only one!

    results = {}

    # TODO Check food_ids from sql output...
    for fi in food_ids:
        result = {}
        for n in zip(field_ids,data):
            result[n[0]] = n[1]

        results[fi] = result

    return results

def sqlInsertMeal(date, meal, food_id, amount):
    sql = "INSERT INTO mealfoods (meal_date, meal, NDB_No, mhectograms) VALUES ("
    sql += repr(date) + ","
    sql += repr(meal) + ","
    sql += repr(food_id) + ","
    sql += repr(amount) + ")"

    cur.execute(sql)
    con.commit()

def sqlGetMealFoods(date):
    sql  = "SELECT food_des.Long_Desc,mealfoods.mhectograms,mealfoods.NDB_No FROM food_des,mealfoods "
    sql += "WHERE mealfoods.meal_date=%d AND mealfoods.NDB_No=food_des.NDB_No" % (date)

    cur.execute(sql)

    result = []

    data = cur.fetchone()
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


layout2 = [ [ "Daily %", [ [  208,  205,  203 ],        # TODO, dit is allemaal special.
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
                           [  601,  430,   -2 ] ] ],

            [ "Nutrients", [ [  208,  205,  203 ],
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
                             [  601,  430,   -2 ] ] ],

            [ "Carbs & Amino Acids", [ [ None, None, None ],
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
                                       [ None, None, None ] ] ],

             [ "Miscellaneous", [ [ None, None, None ],
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
                                  [ None, None, None ] ] ],

             [ "Sat & Mono FA", [ [  606, None ],
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
                                  [  654, None ] ] ],

             [ "Poly & Trans FA", [ [ None, None, None ],
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
                                    [ None, None, None ] ] ]
         ]


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class User:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Has all data concerning the user.
#   Daily Values, Weight, Options
#

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Initialize.
    # Input:
    #   SQL reference
        pass

class nutritionTabs:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Created a notebook with all the nutritionfields in the tabs.
#   Has a update function.

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, layout, user):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Create Notebook
    #       Create Tabs (according to given layout)
    #       Create nutrient fields (according to the given layout)
    #   Store the user for conversions.

        assert type(parent) == gtk.Table

        self.user = user            # TODO Unused.
        self.parent = parent
        self.layout = layout
        self.crossref = []

        # Create notebook.
        self.notebook_widget = gtk.Notebook()

        for tabdata in layout:
            # Create label for tab
            tabnamelabel = gtk.Label()
            tabnamelabel.set_text(tabdata[0])

            # Create content for tab
            tabcontent = gtk.Table()

            # Set size. Need 3 columns for every field.
            rows = len(tabdata[1])
            columns = len(tabdata[1][0])
            tabcontent.resize(columns*3, rows)

            for row in xrange(rows):
                for column in xrange(columns):
                    nutrient_id = tabdata[1][row][column]

                    label_description = gtk.Label()
                    label_value       = gtk.Label()
                    label_units       = gtk.Label()


                    if nutrient_id == None:
                        # Empty field.
                        pass
                    elif nutrient_id < 0:
                        # TODO
                        label_description.set_text("***Special***")
                    else:
                        label_description.set_text(sqlGetNutrName(nutrient_id))
                        label_value.set_alignment(1.0, 0.5)
                        label_units.set_text(" "+sqlGetNutrUnit(nutrient_id))
                        label_units.set_alignment(0.0, 0.5)

                        # Store for later reference.
                        # Note: nutrient_id could be present more than once.
                        self.crossref.append([nutrient_id, label_value])

                    top    = row
                    bottom = row+1
                    left   = column*3
                    right  = column*3+1

                    tabcontent.attach(label_description, left,   right,   top, bottom)
                    tabcontent.attach(label_value,       left+1, right+1, top, bottom)
                    tabcontent.attach(label_units,       left+2, right+2, top, bottom)

            self.notebook_widget.append_page(tabcontent, tabnamelabel)

        parent.attach(self.notebook_widget, 0, 1, 0, 1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sql_update(self, food_id, multiplier):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Retrieve food information from database.
    #   Multiply all ingredients with multiplier and update all fields.
    #   If user is set, use information from there.

        field_ids = []

        for fields in self.crossref:
            if fields[0] not in field_ids:
                field_ids.append(fields[0])

        v = sqlGetFoodNutrientValue(food_id, field_ids)

        for fields in self.crossref:
            label = fields[1]
            value = v[fields[0]]

            if value == None:
                label.set_text("(no data)")
            else:
                s = "%.3f" % (value*multiplier)
                label.set_text(s.rstrip("0").rstrip("."))
                #s = "0"
                #label.set_text(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sql_update_meal(self, mf, mw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   Retrieve food information from database.
    #   Multiply all ingredients with multiplier and update all fields.
    #   If user is set, use information from there.

        field_ids = []

        for fields in self.crossref:
            if fields[0] not in field_ids:
                field_ids.append(fields[0])

        v = sqlGetFoodNutrientValues(mf, field_ids)

        for fields in self.crossref:
            label = fields[1]

            total_value = None
            for fid,weight in zip(mf,mw):
                value = v[fid][fields[0]]
                if value != None:
                    value *= weight
                    if total_value == None:
                        total_value = value
                    else:
                        total_value += value

            if total_value == None:
                label.set_text("(no data)")
            else:
                s = "%.3f" % (total_value)
                label.set_text(s.rstrip("0").rstrip("."))
                #s = "0"
                #label.set_text(s)

    def redraw(self):
        self.notebook_widget.queue_draw()




#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class dateHandler:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Connects to a eventbox/label.
#   Shows the current date, or the date selected.
#

    def __init__(self, builder, parent):

        assert type(parent) == gtk.Table

        eventbox = gtk.EventBox()

        self.date_label = gtk.Label()

        self.selected_date = datetime.datetime.today()

        self.date_label.set_text(self.selected_date.strftime("%e %b %Y"))


        eventbox.connect("button-press-event", self.showCalendar)
        eventbox.add(self.date_label)
        parent.attach(eventbox, 0, 1, 0, 1)

        self.calendarWindow = gtk.Window()
        self.calendarWindow.set_resizable(False)
        self.calendarWindow.set_modal(True)
        self.calendarWindow.set_position(gtk.WIN_POS_MOUSE)
        self.calendarWindow.set_decorated(False)
        self.calendarWindow.set_transient_for(builder.get_object("windowNutMain"))

        self.calendar_widget = gtk.Calendar()
        self.calendar_widget.connect("day-selected-double-click", self.selectDate)

        self.calendar_widget.select_month(self.selected_date.month-1, self.selected_date.year)
        self.calendar_widget.select_day(self.selected_date.day)


        self.calendarWindow.add(self.calendar_widget)

        self.date_set_cb = None


    def showCalendar(self, p1, p2):
        self.calendarWindow.show_all()

    def selectDate(self, p1):
        t = self.calendar_widget.get_date()

        self.selected_date = datetime.datetime(t[0], t[1]+1, t[2])
        self.date_label.set_text(self.selected_date.strftime("%e %b %Y"))

        self.calendarWindow.hide()

        if self.date_set_cb: self.date_set_cb()

    def get_date(self):
        return self.selected_date.year * 10000 + self.selected_date.month * 100 + self.selected_date.day

    def set_date_change_cb(self, f):
        self.date_set_cb = f


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
    #   SQL reference??
    #   Nutrients widget?? or complete builder??

        # Belangrijke zaken
        self.food_id = -1
        self.hgrams = 0.0

        # TODO Temporary?
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

        self.spinbutton = builder.get_object("vf_spinb_amount")
        self.spinbutton.connect("output", self.onSpinB_cb)


        # Setup the search results

        self.ls_search_results = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)

        t = builder.get_object("treeview_vft_searchresult")
        t.set_model(self.ls_search_results)

        column = gtk.TreeViewColumn("Matched foods:")
        t.append_column(column)

        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, "text", 1)

        self.sel_search_results = t.get_selection()

        self.nut_tab = nutritionTabs(builder.get_object("vf_placeholder_nutrients"), layout2, None )
        ### Make all connections

        # Connect search entry
        builder.get_object("entry_vft_search").connect("changed", self.entry_vft_search_changed_cb)

        # Connect search results to update nutrients when chosen
        self.sel_search_results.connect("changed", self.onFoodChanged)

        # Connect add2meal button
        self.builder.get_object("vf_button_add2meal").connect("clicked", self.onAdd2Meal)


        self.builder.get_object("adjustment1").set_all(0.0, 0.0, 0.0, 1.0, 10.0, 0.0)

        self.date = dateHandler(builder, builder.get_object("table_dateselect"))

    def onAdd2Meal(self, button):
        if self.food_id == -1:
            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            message.set_markup("No food item selected.")
            message.run()
            message.destroy()
            return

        if self.hgrams <= 0.0:
            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            message.set_markup("Incorrect amount given.")
            message.run()
            message.destroy()
            return

        # TODO De datum dus... lekker halve dingen doen...
        #
        sqlInsertMeal(self.date.get_date(), 1, self.food_id, self.hgrams);


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def entry_vft_search_changed_cb(self, entry):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose:
    #   If the entered text is >=3 query the database for the foods.

        # Clear list
        self.ls_search_results.clear()

        e = entry.get_text()

        enable = False

        if len(e) >= 3:
            sql = "SELECT NDB_No,Long_Desc FROM food_des WHERE Long_Desc LIKE \"%" + entry.get_text() + "%\""
            cur.execute(sql)

# TODO Vaagheid. Als food-id 14460 erin zit, dan gaat het kapot.
# Zoeken op gat. Iets met
# sqlite3.OperationalError: Could not decode to UTF-8 column 'Long_Desc' with text 'Sports drink, PEPSICO QUAKER GATORADE, GATORADE, original, fruit-flavored, ready-to-drink. Now called G performance O 2.'
#

            while True:
                enable = True
                data = cur.fetchone()
                #print data

                if data == None: break

                #print "type", type(data[0]), " - ", type(data[1])
                i = self.ls_search_results.append()
                self.ls_search_results.set_value(i, 0, data[0])
                self.ls_search_results.set_value(i, 1, data[1])

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
            self.food_id = model.get_value(tree_iter,0)
            value1 = model.get_value(tree_iter,1)

            # Update combobox

            self.ls_combobox.clear()
            w = sqlGetWeightFor(self.food_id)
            for i in w:
                self.ls_combobox.append([i[0], i[1], i[2]])
            self.combobox.set_active(0)
            self.spinbutton.set_value(float(w[0][1]))

            # Set multiplier
            self.hgrams = float(w[0][2])

            self.nut_tab.sql_update(self.food_id, self.hgrams)

        # TODO, adjustment should vary with chosen unit.
        self.builder.get_object("adjustment1").set_all(1.0, 0.0, 1000.0, 1.0, 10.0, 0.0)

    def combobox_changed_cb(self, e):

        assert self.food_id != -1

        a = self.combobox.get_active()

        if a != -1:
            i = self.ls_combobox.get_iter_first()

            for dummy in xrange(a): i = self.ls_combobox.iter_next(i)

            self.spinbutton.set_value(self.ls_combobox.get_value(i, 1))

            assert i != None

            self.hgrams = self.ls_combobox.get_value(i, 2)
            self.nut_tab.sql_update(self.food_id, self.hgrams)


    def onSpinB_cb(self, e):

        # Only do something in a food is selected.
        if self.food_id == -1: return

        # TODO get value is niet goed als je aan het editten bent...
        spv = float( self.spinbutton.get_value() )

        a = self.combobox.get_active()

        if a != -1:
            i = self.ls_combobox.get_iter_first()

            for dummy in xrange(a): i = self.ls_combobox.iter_next(i)

            assert i!= None

            value = self.ls_combobox.get_value(i, 2)
            spv = spv / float(self.ls_combobox.get_value(i, 1))

            self.hgrams = value * spv
            self.nut_tab.sql_update(self.food_id, self.hgrams)

        return False


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class viewMealsTab:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Show the meals, their ingredients and their total nutrients.
#   Not only per meal, but also all for a given day. (=total)
#   Or select from date to date. Then average.

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, builder):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Purpose
    #   etc.
    #   Default: Today, All meals.
    #   Nutrients should be colored?
    #       Red = More than daily allowence (taken from User settings)
    #       Red = More than max. (also taken from user settings, but
    #             most values are presets.?)
    #       Red = Also below RDI.
    #       Green = Within certain range of daily allowance?
    #               ?? Maybe not?
    #       Orange = Nearing red.
    #       Also make tabs with Red items Red
    #
    #   Foods can be changed:
    #       Removed.
    #       Amount changed??

        self.ls_mealfoods = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING)

        t = builder.get_object("treeview_vm_foods")
        t.set_model(self.ls_mealfoods)

        self.sel_mealfoods = t.get_selection()
        self.sel_mealfoods.set_mode(gtk.SELECTION_MULTIPLE)

        column = gtk.TreeViewColumn("Food Item:")
        t.append_column(column)

        cell = gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)

        column = gtk.TreeViewColumn("Weight (g):")
        t.append_column(column)

        cell = gtk.CellRendererText()
        column.pack_start(cell, False)
        column.add_attribute(cell, "text", 1)

        # self.ls_mealfoods dus nog niet vullen.
        # Pas bij de activate.
        # Ofzoiets.
        self.date = dateHandler(builder, builder.get_object("table_dateselect_vm"))

        self.nut_tab = nutritionTabs(builder.get_object("vm_nutrients_placeholder"), layout2, None )


        self.date.set_date_change_cb(self.onView)

        builder.get_object("vm_button_remove").connect("clicked", self.removeFoods)


    def removeFoods(self, p1):
        (model, pathlist) = self.sel_mealfoods.get_selected_rows()

        if len(pathlist) == 0:
            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            message.set_markup("No food item(s) selected.")
            message.run()
            message.destroy()
            return

        for path in pathlist:
            tree_iter = model.get_iter(path)
            print model.get_value(tree_iter,0),
            print model.get_value(tree_iter,1),
            print model.get_value(tree_iter,2)

            self.ls_mealfoods.remove(tree_iter)

        # 

        self.onView()

    def onView(self):
        # Move the filling of information to here.
        # Otherwise startup will take too long?
        mfs = sqlGetMealFoods(self.date.get_date())

        self.ls_mealfoods.clear()

        fid = []
        fw = []
        for mf in mfs:
            fid.append(mf[2])
            fw.append(mf[1])
            self.ls_mealfoods.append([mf[2], "%.2f" % (100.0*float(mf[1])), mf[0] ])


        self.nut_tab.sql_update_meal(fid, fw)



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class nutWindowHandlers:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   Catch all handlers defined via glade.
#

    def __init__(self):
        self.aboutwindow = builder.get_object("aboutdialog1")
        self.aboutwindow.connect("response", self.closeAbout)

    def windowNutMain_delete_event_cb(self, *args):
        gtk.main_quit(args)

    def windowShowDialog(self, *arg):
        self.aboutwindow.show_all()

    def closeAbout(self, *args):
        self.aboutwindow.hide()

def doubleclick(p1):

    print p1

    cw = builder.get_object("calendar1")
    print cw.get_date()

    window = builder.get_object("windowCalendar")
    window.hide()

def showDataTime(p1, p2):

    print p1
    print p2

    print "xxx"
    window = builder.get_object("windowCalendar")

    cw = builder.get_object("calendar1")
    cw.connect("day-selected-double-click", doubleclick)

    window.show()


    # Wait??



builder = gtk.Builder()


class topNotebook:
    def __init__(self, builder):

        self.vf = viewfoodTab(builder)
        self.vm = viewMealsTab(builder)


        builder.get_object("notebook3").connect("switch-page", self.noteBookChange)


    def noteBookChange(self, p1, p2, p3):

        # TODO This should be done better...
        if p3 == 1: self.vm.onView()
        

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def nutMain():
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Purpose:
#   BLA
#   bla
#   bla
#

    builder.add_from_file("nut_try.glade")

    builder.connect_signals(nutWindowHandlers())


    zzz = topNotebook(builder)

    # Show off
    window = builder.get_object("windowNutMain")
    window.show_all()
    gtk.main()



nutMain()
