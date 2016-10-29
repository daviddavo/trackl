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
import os, sys, logging, time, re
import xml.etree.ElementTree as xmltree
import urllib.request
import json

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
        self.tracker = tracker.Tracker(self, percentage=60, wait_s=10)

    def show_watched(self):
        self.tree_dic = dict()
        show_color = "#3F51B5"
        movie_color = "#1B5E20"
        anime_color = "#3F51B5" #CURRENTLY NOT IN USE

        def sortf(model, row1, row2, user_data):
            nohtml = re.compile("<.*?>")
            sort_column, _ = model.get_sort_column_id()
            value1 = re.sub(nohtml, "", model.get_value(row1, sort_column))
            value2 = re.sub(nohtml, "", model.get_value(row2, sort_column))
            if value1 < value2:
                return -1
            elif value1 == value2:
                return 0
            else:
                return 1

        for each in ["watching", "completed", "plantowatch", "dropped"]:
            self.tree_dic[each] = (builder.get_object(each + "-treeview"),
                Gtk.ListStore(str, str, str, str, str))
            #0 for TreeView, 1 for ListStore
            self.tree_dic[each][0].set_model(self.tree_dic[each][1])
            self.tree_dic[each][1].set_sort_func(0, sortf, None)


        for tree in self.tree_dic.values():
            for i, column_title in enumerate(["Title", "Last Seen", "Score",
                "Status", "Type"]):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i, markup=i)
                column.set_sort_column_id(i)
                column.set_resizable(True)
                tree[0].append_column(column)
                #renderer.set_property("foreground", show_color)

        wdic = self.engine.wdic
        with open("tmp.json", "w") as f:
            f.write(json.dumps(wdic, indent=2))
        print(wdic)
        for x in wdic:
            for lst in wdic[x]:
                #print(lst)
                st = [x for x in list(lst.keys()) if x in ["movie", "show"]][0]
                logging.debug(lst[st])
                nxt = "None" #Last seen episodes
                if st == "show" and lst["status"] == "watching":
                    #print("\n",lst["seasons"])
                    try:
                        season  = max( [x["number"] for x in lst["seasons"]] )
                        episode = max( [x["number"] for x in lst["seasons"][season-1]["episodes"]] )
                    except:
                        season  = "00"
                        episode = "RROR"
                if st=="show":
                    nxt = lst["last_watched"]

                tmplst = [
                    lst[st]['title'], nxt, str(lst["user_rating"]), lst["status"], st
                ]
                #print(tmplst)
                for i,ls in enumerate(tmplst):
                    color = show_color
                    if st == "movie":
                        color = movie_color
                    tmplst[i] = "<span color='{}'>{}</span>".format(color, ls)
                #print(tmplst)
                row = self.tree_dic[lst["status"]][1].append(tmplst)

        def on_select(widget, *args):
            tmpdic = {"watching":0, "completed":1, "plantowatch":2, "dropped":3}
            treeview = widget.get_tree_view()

            nohtml = re.compile("<.*?>")
            showname = re.sub(nohtml, "", treeview.get_model().get_value(widget.get_selected()[1],0))
            rate = treeview.get_model().get_value(widget.get_selected()[1],2)
            builder.get_object("label-showname").set_text(showname)
            status = treeview.get_model().get_value(widget.get_selected()[1],3)
            status = re.sub(nohtml, "", status)
            builder.get_object("combobox-status").set_active(tmpdic[status])
            spinbutton  = builder.get_object("score-spinbutton")
            spinadjust = spinbutton.get_adjustment()
            spinadjust.set_value(8)
            spinbutton.set_value(8)
            try:
                pass
            except:
                builder.get_object("score-spinbutton").set_value()

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
            
            infobar.set_tooltip_text("Scrobbling on {}%".format(self.tracker.percentage))

        else:
            logging.debug("SCROBBLED" + txt)
            print("SCROBBLED")
            if infobar.get_message_type() != Gtk.MessageType.INFO:
                infobar.set_message_type(Gtk.MessageType.INFO)
            infobar.set_tooltip_text("Scrobbled")
        
        label.set_text(str(txt.replace("\n", " ")))

        progressbar.set_fraction(min(1, percent/100))
        progressbar.set_text(str(min(100,round(percent,3))) + "%")
        
        print("IBR:", infobar.get_message_type())

    def send_to_statusbar(self, txt):
        stbar = builder.get_object("statusbar")
        stbar.push(0, txt)

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

def main():
    if apiconnect.logged == False:
        print("Logging in")
    else:
        w = mainWindow()
        w.mainwindow.show_all()

        #w = loginWindow()
        #print(w.run())
    Gtk.main()
if __name__ == "__main__":
    main()