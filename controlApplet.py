#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import gettext
import os
import gnome
import time
import gconf_prefs
import gobject
import sys
import gnomeapplet
import mouse


# Multi-lingual support
_ = gettext.gettext

gobject.threads_init()


# globals
name = "Control Applet"
version = "0.1"
control_image="/usr/share/pixmaps/arrows.png"
puntero = mouse.Mouse()

class boton(gtk.Button):
    
    def __init__(self, stock, action, label = None, use_label = False, focus_color = "#FF0000", active_color = "#00FF00", inactive_color = "#0000FF"):
        gtk.Button.__init__(self, stock = stock)
        if label and use_label: 
            self.set_label(label)
        else:
            Label=self.get_children()[0]
            Label.get_children()[0].get_children()[1].set_label('')
        self.action = action
        self.modify_bg(gtk.STATE_NORMAL, self.get_colormap().alloc_color(inactive_color))
        self.modify_bg(gtk.STATE_SELECTED, self.get_colormap().alloc_color(focus_color))
        self.modify_bg(gtk.STATE_ACTIVE, self.get_colormap().alloc_color(active_color))
        self.set_sensitive(False)
        #self.connect("focus", self.focus_in)
        
        
    def set_action(self, scroll = 1):
        global puntero
        puntero.wait_clic = 0
        if self.action == "up":
            puntero.set_scroll(-scroll)
            puntero.direccion = True
        elif self.action == "down":
            puntero.set_scroll(scroll)
            puntero.direccion = True
        elif self.action == "left":
            puntero.set_scroll(-scroll)
            puntero.direccion = False
        elif self.action == "right":
            puntero.set_scroll(scroll)
            puntero.direccion = False
        elif self.action == "button1":
            puntero.set_scroll(0)
            puntero.wait_clic = 1
        elif self.action == "button3":
            puntero.set_scroll(0)
            puntero.wait_clic = 3
        elif self.action == "double_clic":
            puntero.set_scroll(0)
            puntero.wait_clic = 2
            
            
            
    def focus_in(self, widget, event):
        print "focus"
        self.modify_bg(gtk.STATE_NORMAL, self.get_colormap().alloc_color(self.focus_color))
        self.show()
        
    def focus_out(self):
        print "no focus"
        self.modify_bg(gtk.STATE_NORMAL, self.get_colormap().alloc_color(self.inactive_color))
        self.show()

class controlApplet(gnomeapplet.Applet):

    def cleanup(self,event):
        global puntero
        puntero.join()
        del puntero
        del self.applet

    def change_orientation(self,arg1,data):
        self.orientation = self.applet.get_orient()

        if self.orientation == gnomeapplet.ORIENT_UP or self.orientation == gnomeapplet.ORIENT_DOWN:
            tmpbox = gtk.HBox()
        else:
            tmpbox = gtk.VBox()
        # reparent all the widgets to the new tmpbox
        widgets = self.box.get_children()
        for w in widgets:
            #self.box.remove(w)
            #tmpbox.pack_start(w)
            w.reparent(tmpbox)
        self.applet.remove(self.box)
        self.box = tmpbox
        tmpbox.show()
        self.applet.add(self.box)
        self.applet.show_all()

    # this callback is to create the context menu
    def applet_press(self,widget,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.create_menu()
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            if self.running:
                self.stop()
            else:
                self.run()
            self.running = not self.running

    # and this one to show the about box
    def about_info(self,event,data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name(name)
        dialog.set_version(version)
        dialog.set_copyright("Copyright © 2007 Fernando Ruiz")
        dialog.set_authors([
            _("Programadores") + ':',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
        ])
        dialog.set_artists([_("Diseñado gráfico") + ':',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
        ])
        dialog.set_translator_credits(_("Este programa aún no ha sido traducido a otros idiomas"))
        logo_file = os.path.abspath(jump_image)
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_("Applet para registrar las pulsaciones del ratón"))
        dialog.run()
        dialog.destroy()

    # the preferences one
    def properties(self,event,data=None):
        preferences = gtk.Dialog(_("Preferencias"), None,
         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        preferences.set_has_separator(True)
        logoad = gtk.Image()
        iconad = preferences.render_icon(gtk.STOCK_PREFERENCES, 1)
        
        adj = gtk.Adjustment(self.config["espera"], 1.0, 10.0, 1.0, 2.0, 0.0)
        espera = gtk.SpinButton(adjustment=adj, climb_rate=0.10, digits=2)
        adj = gtk.Adjustment(self.config["intervalo"], 10.0, 5000.0, 10.0, 50.0, 0.0)
        timeout = gtk.SpinButton(adjustment=adj, climb_rate=0.25, digits=0)
        check_autostart = gtk.CheckButton(label=_("Iniciar automáticamente"))
        check_autostart.set_active(self.config["autostart"])
        
        
        preferences.vbox.pack_start(gtk.Label(_("Configuración del programa")), True, True, 5)
       
        h2 = gtk.HBox()
        
        h2.pack_start(gtk.Label(_("Intervalo entre opciones (ms)")), True, True, 0)
        h2.pack_start(timeout, False, False, 3)
        preferences.vbox.pack_start(h2, True, True, 0)
       
        preferences.vbox.pack_start(check_autostart)
        
        preferences.show_all()
        response = preferences.run()
        if response == gtk.RESPONSE_ACCEPT:
            
            self.config["intervalo"] = timeout.get_value_as_int()
            
            self.config["autostart"] = check_autostart.get_active()
            #print self.config
            self.prefs.gconf_update_config(self.config)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        preferences.destroy()

    # this callback is to create a context menu with the second button
    def create_menu(self):
        self.applet.setup_menu(self.propxml,self.verbs,None)


    # preferences window callbacks
    def on_properties_delete_event(self,widget,event):
        widget.hide()
        return gtk.TRUE

    # add widgets to the applet
    def insert(self, widget):
        self.box.pack_start(widget)
        self.box.show_all()
    
    def run(self):
        print "corriendo"
        global puntero
        self.avance = puntero.avance
        puntero.set_action("pause")
        puntero.grab_keys(65,36)
        self.set_focus()
        
    def stop(self):
        print "parado"
        global puntero
        puntero.ungrab_keys()
        puntero.set_action("pause")
        puntero.set_scroll(self.avance)
        self.stop_timer()
        self.box.get_children()[self.focused-1].set_sensitive(False)
    
    def stop_timer(self):
        gobject.source_remove(self.timer)
         
    def set_focus(self):
        self.timer = gobject.timeout_add(self.config["intervalo"], self.set_focus)
        global puntero
        if puntero.action == "pause":
            childrens = self.box.get_children()
            if self.focused >= len(childrens):
                childrens[self.focused - 1].set_sensitive(False)
                self.focused = 1
            if self.focused - 1:
                childrens[self.focused - 1].set_sensitive(False)
                
            self.box.set_focus_child(childrens[self.focused])
            childrens[self.focused].set_sensitive(True)
            childrens[self.focused].set_action(self.avance)

            self.focused += 1
            self.box.show_all()

    # the __init__ method
    def __init__(self,applet,iid):

        # do it a gobject.
        self.__gobject_init__()
        
        self.running = False
        self.timer = None
        self.focused = 1
        self.avance = None
         # config values
        self.config={
        "intervalo":1000, \
        "espera" :1.0, \
        "autostart" :  False     
        }
        self.gconfkey = '/apps/control_applet/'
        self.prefs = gconf_prefs.AutoPrefs(self.gconfkey, self.config)
        self.config = self.prefs.gconf_load()
        if self.prefs.first_run:
            self.prefs.gconf_save() 

        self.tooltip_text = ""

        self.orientation = gnomeapplet.ORIENT_DOWN
        
        self.propxml="""
        <popup name="button3">
        <menuitem name="Item 1" verb="Props" label="_Preferencias" pixtype="stock" pixname="gtk-properties"/>
        <menuitem name="Item 2" verb="About" label="_Acerca de" pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
        """

        self.verbs = [  ( "Props", self.properties ),
                        ( "About", self.about_info )
                 ]

        # initialize gnome application and set up all the gnome internals
        gnome.init(name, version)

        # create the applet and the widgets
        self.applet = applet

        self.orientation = self.applet.get_orient()

        self.box = None
        # if we have an horizontal panel
        if self.orientation == gnomeapplet.ORIENT_UP or self.orientation == gnomeapplet.ORIENT_DOWN:
            self.box = gtk.HBox()
        # if it's a vertical one
        else:
            self.box = gtk.VBox()

        # create the applet with little hboxes containing each info checked in the preferences
        self.box.show()
        self.applet.add(self.box)
       
        # create especific widgets
        self.logo_pixbuf = gtk.gdk.pixbuf_new_from_file(control_image)
        image = gtk.Image()
        image.set_from_pixbuf(self.logo_pixbuf)
        self.box.pack_start(image)
        self.tittle = gtk.Label(name)
        self.up = boton(gtk.STOCK_GO_UP, 'up')
        self.down = boton(gtk.STOCK_GO_DOWN, 'down')
        self.left = boton(gtk.STOCK_GO_BACK, 'left')
        self.right = boton(gtk.STOCK_GO_FORWARD, 'right')
        self.button1 = boton(None, 'button1', "Izq", True)
        self.dobleclic = boton(None, 'double_clic', "2 Clic", True)
        self.button3 = boton(None, 'button3', "Der", True)
        
        
        # add widgets
        
        self.box.pack_start(self.left)
        self.box.pack_start(self.right)
        self.box.pack_start(self.up)
        self.box.pack_start(self.down)
        self.box.pack_start(self.button1)
        self.box.pack_start(self.dobleclic)
        self.box.pack_start(self.button3)
        

        
        # connect some signals to the applet/widgets
        self.applet.connect("button-press-event",self.applet_press)
        self.applet.connect("change-orient",self.change_orientation)
        self.applet.connect("delete-event",self.cleanup)
        #self.play.connect("clicked",self.run)
        #self.record.connect("clicked",self.run)

        
        if self.config["autostart"]:
            self.running = True
            self.run()
        self.applet.show_all()


gobject.type_register(controlApplet)

# bonobo factory of baseApplets
def control_applet_factory(applet, iid):
    global puntero
    puntero.set_action("pause")
    puntero.start()
    controlApplet(applet,iid)
    return gtk.TRUE

# run it in a gtk window
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Debugger mode")
    main_window.set_decorated(False)
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    control_applet_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:GNOME_ControlApplet_Factory",
                                controlApplet.__gtype__,
                                "hello", "0", control_applet_factory)
 


