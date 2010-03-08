#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import sys
import pygtk
pygtk.require('2.0')
import gtk
import gnomeapplet
import gnome
import gobject
import gettext
import os
import time
import gconf_prefs
import mouse

# Multi-lingual support
_ = gettext.gettext

gobject.threads_init()


# globals
name = "Scan Applet"
version = "0.1"
scan_image="/usr/share/icons/gnome/24x24/devices/input-mouse.png"
animation="/usr/share/pixmaps/scan.gif"
puntero = mouse.Mouse()


class scanApplet(gnomeapplet.Applet):

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
                
    def run(self):
        global puntero
        puntero.grab_keys(36, 22)
        puntero.set_action("scan")
        puntero.progresivo = self.config["progresivo"]
        puntero.set_time_wait(self.config["espera"])
        puntero.set_scroll(self.config["avance"])
        puntero.return_origin = self.config["volver_inicio"]
        puntero.ralentizacion = self.config["ralentizacion"]
        self.running = True
        #self.b.set_label("Barriendo...")
        self.logo_state.set_from_animation(self.logo_running)
        

    def stop(self):
        #self.b.set_label("Parado")
        puntero.ungrab_keys()
        puntero.set_action("pause")
        self.running = False
        self.logo_state.set_from_stock(gtk.STOCK_NO, 1)

        
    

    # and this one to show the about box
    def about_info(self,event,data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name(name)
        dialog.set_version(version)
        dialog.set_copyright("Copyright © 2007 Fernando Ruiz")
        dialog.set_authors([
            _("Programadores") + ':',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
            'Javier Muñoz Díaz <javier.munoz@cofiman.es>\n'
        ])
        dialog.set_artists([_("Diseñado gráfico") + ':',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
        ])
        dialog.set_translator_credits(_("Este programa aún no ha sido traducido a otros idiomas"))
        logo_file = os.path.abspath(scan_image)
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_("Applet para el movimiento automático del puntero"))
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
        adj = gtk.Adjustment(self.config["avance"], 1.0, 100.0, 2.0, 10.0, 0.0)
        avance = gtk.SpinButton(adjustment=adj, climb_rate=0.025, digits=0)
        adj = gtk.Adjustment(self.config["espera"], 0.01, 5.0, 0.01, 0.10, 0.0)
        espera = gtk.SpinButton(adjustment=adj, climb_rate=0.050, digits=2)
        adj = gtk.Adjustment(self.config["ralentizacion"]*100, 10.0, 100.0, 10.0, 20.0, 0.0)
        ralentizacion = gtk.SpinButton(adjustment=adj, climb_rate=0.025, digits=0)
        check_progresivo = gtk.CheckButton(label=_("Barrido progresivo"))
        check_progresivo.set_active(self.config["progresivo"])
        check_autostart = gtk.CheckButton(label=_("Iniciar automáticamente"))
        check_autostart.set_active(self.config["autostart"])
        check_reiniciar = gtk.CheckButton(label=_("Volver al origen"))
        check_reiniciar.set_active(self.config["volver_inicio"])
        
        preferences.vbox.pack_start(gtk.Label(_("Configuración del programa")), True, True, 5)
        h1 = gtk.HBox()
        h2 = gtk.HBox()
        h3 = gtk.HBox()
        h1.pack_start(gtk.Label(_("Avance del puntero (px)")), True, True, 0)
        h1.pack_start(avance, False, False, 3)
        h2.pack_start(gtk.Label(_("Intervalo entre movimientos (ms)")), True, True, 0)
        h2.pack_start(espera, False, False, 3)
        h3.pack_start(gtk.Label(_("Velocidad ralentizada (%)")), True, True, 0)
        h3.pack_start(ralentizacion, False, False, 3)
        preferences.vbox.pack_start(h1, True, True, 0)
        preferences.vbox.pack_start(h2, True, True, 0)
        preferences.vbox.pack_start(h3, True, True, 0)
        preferences.vbox.pack_start(check_progresivo)
        preferences.vbox.pack_start(check_autostart)
        preferences.vbox.pack_start(check_reiniciar)
        preferences.show_all()
        response = preferences.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.config["avance"] = avance.get_value()
            self.config["espera"] = espera.get_value()
            self.config["ralentizacion"] = ralentizacion.get_value()/100
            self.config["progresivo"] = check_progresivo.get_active()
            self.config["autostart"] = check_autostart.get_active()
            self.config["volver_inicio"] = check_reiniciar.get_active()
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

    # the __init__ method
    def __init__(self, applet, iid):

        # do it a gobject.
        self.__gobject_init__()
        self.timeout_interval = 1000
        self.tooltip_text = ""

        self.orientation = gnomeapplet.ORIENT_DOWN
        self.logo_pixbuf = None
        
        self.propxml="""
        <popup name="button3">
        <menuitem name="Item 1" verb="Props" label="_Preferencias" pixtype="stock" pixname="gtk-properties"/>
        <menuitem name="Item 2" verb="About" label="_Acerca de" pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
        """

        self.verbs = [ ( "Props", self.properties ),
                       ( "About", self.about_info )
                 ]
        self.running = False
        
        # config values
        self.config={
        "espera" :0.02, \
        "avance" : 4,\
        "ralentizacion" : 0.5,\
        "progresivo" : True,\
        "volver_inicio" : True,\
        "autostart" :  False     
        }
        self.gconfkey = '/apps/scan_applet/'
        self.prefs = gconf_prefs.AutoPrefs(self.gconfkey, self.config)
        self.config = self.prefs.gconf_load()
        if self.prefs.first_run:
            self.prefs.gconf_save()     
        
        # initialize gnome application and set up all the gnome internals
        gnome.init("Prueba de scan", "0.1")

        # create the logo from file 
        self.logo_pixbuf = gtk.gdk.pixbuf_new_from_file(scan_image)

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
        image = gtk.Image()
        image.set_from_pixbuf(self.logo_pixbuf)
        self.box.pack_start(image)
        self.logo_state = gtk.Image()
        self.logo_running = gtk.gdk.PixbufAnimation(animation)
        #self.logo_state.set_from_animation(self.logo_running)
        self.logo_state.set_from_stock(gtk.STOCK_NO, 1)
        self.box.pack_start(self.logo_state)
        #self.b = gtk.Label("Barrido de pantalla")
        #self.box.pack_start(self.b)
        self.box.show()
        self.applet.add(self.box)

        # connect some signals to the applet
        self.applet.connect("button-press-event",self.applet_press)
        self.applet.connect("change-orient",self.change_orientation)
        self.applet.connect("delete-event",self.cleanup)
        
        if self.config["autostart"]:
            self.run()
            self.running = True
        self.applet.show_all()


gobject.type_register(scanApplet)

# bonobo factory of scanApplets
def scan_applet_factory(applet, iid):
    global puntero
    puntero.set_action("pause")
    puntero.start()
    scanApplet(applet, iid)
    
    return gtk.TRUE

# run it in a gtk window
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_keep_above(True)
    main_window.set_decorated(False)
    main_window.set_title("Debugger mode")
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    scan_applet_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:GNOME_ScanApplet_Factory",
                                scanApplet.__gtype__,
                                "hello", "0", scan_applet_factory)


