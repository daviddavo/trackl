'''
    Trackl: Multiplatform simkl tracker
    Copyright (C) 2016  David Davó   david@ddavo.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os, sys, logging
import xml.etree.ElementTree as xmltree

from trackl import tracker
from trackl import apiconnect

trackl_configdir = os.path.expanduser("~/.config/trackl")
logging.basicConfig(filename=trackl_configdir + "/log.log", level=logging.DEBUG)
logging.debug("gtk loaded")

try:
    #Importando las dependencias de la interfaz
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
except:
    lprint("Por favor, instala PyGObject en tu ordenador. \n  En ubuntu suele ser 'apt-get install python3-gi'\n  En Archlinux es 'pacman -S python-gobject'")
    sys.exit()

maindir, this_filename = os.path.split(__file__)
gladefile = maindir + "/Gtk.glade"

try:
    builder = Gtk.Builder()
    builder.add_from_file(gladefile)
    xmlroot = xmltree.parse(gladefile).getroot()
    print("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0", end="")
    print(" | Usando Gtk+ "+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
except Exception as e:
    print("Error: No se ha podido cargar la interfaz.")
    if "required" in str(e):
        xmlroot = xmltree.parse(gladefile).getroot()
        print("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0", end="\n")
        print(">Estas usando Gtk+"+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
    else:
        print("Debug:", e)
    sys.exit()

class mainWindow(Gtk.Window):
    def __init__(self):
        print("Starting interface")
        self.mainwindow = builder.get_object("MainWindow")

        handlers = {
        "onDeleteWindow":   exit,
        }
        builder.connect_signals(handlers)

        self.mainwindow.show_all()
        self.engine = apiconnect.Engine()
        self.show_watched()
        builder.get_object("label-username").set_text(apiconnect.username)

    def show_watched(self):
        self.watching_TreeView = builder.get_object("watching-treeview")
        self.watching_store = Gtk.ListStore(str, str, str, str)
        self.watching_TreeView.set_model(self.watching_store)
        self.completed_TreeView = builder.get_object("completed-treeview")
        self.completed_store = Gtk.ListStore(str,str,str,str)
        self.completed_TreeView.set_model(self.completed_store)
        self.ptw_TreeView = builder.get_object("ptw-treeview")
        self.ptw_store = Gtk.ListStore(str,str,str,str)
        self.ptw_TreeView.set_model(self.ptw_store)
        self.dropped_TreeView = builder.get_object("dropped-treeview")
        self.dropped_store = Gtk.ListStore(str,str,str,str)
        self.dropped_TreeView.set_model(self.dropped_store)

        for i, column_title in enumerate(["Title", "Next", "Status", "Type"]):
            for j in [self.watching_TreeView, self.completed_TreeView, 
                self.ptw_TreeView, self.dropped_TreeView]:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                column.set_sort_column_id(i)
                j.append_column(column)

        wdic = self.engine.get_watched("")
        #print(wdic)
        for x in wdic:
            for lst in wdic[x]:
                #print(lst)
                st = [x for x in list(lst.keys()) if x in ["movie", "show"]][0]
                nxt = "None"
                if not st == "movie":
                    nxt == "S{}E{}"
                tmplst = [
                    lst[st]['title'], nxt, lst[st]["status"], st
                ]
                #print(tmplst)
                if lst[st]["status"] == "watching":
                    row = self.watching_store.append(tmplst)
                elif lst[st]["status"] == "completed":
                    row = self.completed_store.append(tmplst)
                elif lst[st]["status"] == "plantowatch":
                    row = self.ptw_store.append(tmplst)
                elif lst[st]["status"] == "dropped":
                    row = self.dropped_store.append(tmplst)

        self.watching_TreeView.show_all()
        self.completed_TreeView.show_all()
        self.ptw_TreeView.show_all()
        #row = self.store.append(lst)

class loginWindow(Gtk.Dialog):
    def __init__(self):
        daemonfile = maindir + "/Daemon.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(daemonfile) #Temp fix until I do the full interface
        self.mainw = self.builder.get_object("login_window")

        self.submitbutton = self.builder.get_object("submit-button")
        self.submitbutton.connect("clicked", self.mainw.hide)

    def run(self):
        r = self.mainw.run()
        print(self.builder.get_object("entry_mail"))
        mail     = self.builder.get_object("entry_mail").get_text()
        password = self.builder.get_object("entry_password").get_text()
        self.destroy()
        return mail, password
        
    def destroy(self):
        self.mainw.destroy()

class daemonWindow(Gtk.Window):
    pass

def exit(*args):
    print("Window closed, exiting program")
    Gtk.main_quit()

if __name__ == "__main__":
    if apiconnect.logged == False:
        print("Logging in")
    else:
        w = mainWindow()
        w.mainwindow.show_all()

        #w = loginWindow()
        #print(w.run())
    Gtk.main()