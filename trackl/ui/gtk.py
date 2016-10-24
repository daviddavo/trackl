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
import os, sys, logging,time
import xml.etree.ElementTree as xmltree
import urllib.request

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
    from gi.repository.GdkPixbuf import Pixbuf
except Exception:
    lprint("Por favor, instala PyGObject en tu ordenador. \n  En ubuntu suele ser 'apt-get install python3-gi'\n  En Archlinux es 'pacman -S python-gobject'")
    logging.ERROR(Exception)
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
    allkeys = set()
    def __init__(self):
        print("Starting interface")
        self.mainwindow = builder.get_object("MainWindow")
        self.mainwindow.connect("key-press-event", self.on_key_press_event)
        self.mainwindow.connect("key-release-event", self.on_key_realease_event)

        handlers = {
        "onDeleteWindow":   exit,
        }
        builder.connect_signals(handlers)

        self.mainwindow.show_all()
        self.engine = apiconnect.Engine()
        self.show_watched()
        builder.get_object("label-username").set_text(apiconnect.username)
        self.tracker = tracker.Tracker(self, percentage=70, wait_s=10)

    def show_watched(self):
        self.tree_dic = dict()
        for each in ["watching", "completed", "plantowatch", "dropped"]:
            self.tree_dic[each] = (builder.get_object(each + "-treeview"),
                Gtk.ListStore(str, str, str, str, str))
            self.tree_dic[each][0].set_model(self.tree_dic[each][1])

        for i, column_title in enumerate(["Title", "Next", "Score",
            "Status", "Type"]):
            for row in self.tree_dic.values():
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                column.set_sort_column_id(i)
                row[0].append_column(column)

        wdic = self.engine.get_watched("")
        #print(wdic)
        for x in wdic:
            for lst in wdic[x]:
                #print(lst)
                st = [x for x in list(lst.keys()) if x in ["movie", "show"]][0]
                logging.debug(lst[st])
                nxt = "None"
                if not st == "movie":
                    nxt = "S{SEASON}E{EPISODE}"
                tmplst = [
                    lst[st]['title'], nxt, str(lst[st]["rate"]), lst[st]["status"], st
                ]
                #print(tmplst)
                row = self.tree_dic[lst[st]["status"]][1].append(tmplst)

        def on_select(widget, *args):
            treeview = widget.get_tree_view()

            showname = treeview.get_model().get_value(widget.get_selected()[1],0)
            rate = treeview.get_model().get_value(widget.get_selected()[1],2)
            builder.get_object("label-showname").set_text(showname)
            builder.get_object("label-rating").set_text("  " + rate + "  ")

            '''
            url = "http://3g28wn33sno63ljjq514qr87.wpengine.netdna-cdn.com/wp-content/uploads/2015/10/Star-Wars-Poster-700x1068.jpg"
            response = urllib.request.urlopen(url)
            fname =  trackl_configdir + "/images/"+ url.split("/")[-1]
            f = open(fname, "wb")
            f.write(response.read())
            f.close()
            response.close()
            image = builder.get_object("show_image")
            pixbuf = Pixbuf.new_from_file(fname)
            pixbuf = pixbuf.scale_simple(100, 150, GdkPixbuf.InterpType.BILINEAR)
            image.set_from_pixbuf(pixbuf)
            '''

        for val,key in self.tree_dic.items():
            key[0].show_all()
            select = key[0].get_selection()
            select.connect("changed", on_select)

    def on_key_press_event(self, widget, event):
        keyname = event.keyval
        print(keyname, Gdk.keyval_name(keyname))
        aks = self.__class__.allkeys
        nb = builder.get_object("mainnotebook")
        if not keyname in aks:
            aks.add(int(keyname))

        if (65056 in aks) and (65507 in aks):
            nb.prev_page()
        elif (65507 in aks) and (65289 in aks):
            nb.next_page()
        if 65507 in aks and 113 in aks:
            exit()
        elif 65507 in aks and 114 in aks:
            restart()

    def on_key_realease_event(self,widget,event):
        aks = self.__class__.allkeys
        aks.remove(event.keyval)

    def _update_scrobbling(self, txt, percent=0,finished=False):
        infobar = builder.get_object("infobar")
        inforevealer = builder.get_object("inforevealer")
        progressbar = builder.get_object("infobar_progress")
        label = builder.get_object("infobar_label")

        if False == inforevealer.get_reveal_child() and percent >= 0:
            time.sleep(.1)
            inforevealer.set_reveal_child(True)
        elif inforevealer.get_reveal_child() and percent < 0:
            time.sleep(.1)
            inforevealer.set_reveal_child(False)

        if not finished:
            if infobar.get_message_type() != Gtk.MessageType.WARNING:
                infobar.set_message_type(Gtk.MessageType.WARNING)
            
            progressbar.set_tooltip_text("Scrobbling on {}%".format(self.tracker.percentage))

        else:
            logging.debug("SCROBBLED" + txt)
            print("SCROBBLED")
            if infobar.get_message_type() != Gtk.MessageType.INFO:
                infobar.set_message_type(Gtk.MessageType.INFO)
            progressbar.set_tooltip_text("Scrobbled")
        
        label.set_text(str(txt.replace("\n", " ")))

        progressbar.set_fraction(percent/100)
        
        print("IBR:", infobar.get_message_type())

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

def restart(*args):
    os.execl(sys.executable, sys.executable, *sys.argv)

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