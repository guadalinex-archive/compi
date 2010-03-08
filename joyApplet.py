#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import signal
import sys
import gnomeapplet
import gnome
import gettext
import gconf_prefs

# Multi-lingual support
_ = gettext.gettext


# globals
name = "Joymouse Applet"
version = "0.1"
joystick_image="/usr/share/icons/crystalsvg/22x22/devices/joystick.png"


class joyApplet(gnomeapplet.Applet):

    def cleanup(self,event):
        self.stop()
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
        logo_file = os.path.abspath(joystick_image)
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_("Applet para controlar el puntero mediante un Joystick"))
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
        tipo = gtk.Combo()
        tipo.set_popdown_strings(self.game_controllers)
        tipo.entry.set_text(self.config["type"])
        device = gtk.Entry()
        device.set_text(self.config["device"])
        check_autodetect = gtk.CheckButton(label=_("Autodetectar dispositivo"))
        check_autodetect.set_active(self.config["autodetect"])
        check_autostart = gtk.CheckButton(label=_("Iniciar automáticamente"))
        check_autostart.set_active(self.config["autostart"])
        preferences.vbox.pack_start(gtk.Label(_("Configuración del programa")), True, True, 5)
        h1 = gtk.HBox()
        h2 = gtk.HBox()
        h3 = gtk.HBox()
        h1.pack_start(gtk.Label(_("Tipo de controlador")), True, True, 0)
        h1.pack_start(tipo, False, False, 3)
        h3.pack_start(gtk.Label(_("Dispositivo")), True, True, 0)
        h3.pack_start(device, False, False, 3)
        preferences.vbox.pack_start(h1, True, True, 0)
        #preferences.vbox.pack_start(h2, True, True, 0)
        preferences.vbox.pack_start(h3, True, True, 0)
        preferences.vbox.pack_start(check_autodetect)
        preferences.vbox.pack_start(check_autostart)
        preferences.show_all()
        response = preferences.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.config["device"] = device.get_text()
            self.config["type"] = tipo.entry.get_text()
            self.config["autodetect"] = check_autodetect.get_active()
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
        signal.signal(signal.SIGCHLD,signal.SIG_IGN)
        if not self.config["device"] and self.config["type"].startswith("joy"):
            for i in range(4):
                dev = "/dev/input/js%d" %i
                if os.path.exists(dev):
                    self.config["device"] = dev
                    print "Encontrado", dev
            if not self.config["device"]:
                aviso = gtk.Dialog("Información", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                aviso.vbox.pack_start(gtk.Label( _("No se ha detectado ningún dispositivo válido conectado.")))
                aviso.show_all()
                response = aviso.run()
                aviso.destroy()
                return 0
        if self.config["type"] == "wiimote":
            if os.path.exists("/usr/bin/wminput"):
                mensaje = _("Active el modo descubrimiento de su Wiimote pulsando 1 + 2.")
            else:
                mensaje = _("Instale primero el programa 'wminput'.")
            aviso = gtk.Dialog("Información", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            aviso.vbox.pack_start(gtk.Label(mensaje))
            aviso.show_all()
            response = aviso.run()
            aviso.destroy()
            
        self.pid = os.fork()
        if not self.pid:
            if self.config["type"] == "wiimote":
                try:
                    os.execv(self.path["wminput"], ["wminput", "-c", "ir_ptr"])
                except:
                    print "Error al iniciar wminput"
                    sys.exit(0) 
                sys.exit(1) 
            else:
                try:
                    if os.path.exists(self.config["device"]):
                        
                        os.execv(self.path["joymouse"], ["joymouse", "-i" , self.config["device"],
                                            "-t", self.config["type"]])
                    else:
                        sys.exit(0) 
                except:
                    print "Error al iniciar joymouse"
                    sys.exit(0) 
                    
                sys.exit(1)
        else:
            self.timer = gobject.timeout_add(1, self.check_status)
            
    def check_status(self):
        try:
            os.waitpid(self.pid, os.WNOHANG)
            self.timer = gobject.timeout_add(1, self.check_status)
            self.logo_state.set_from_stock(gtk.STOCK_YES, 1)
            self.running = True
        except:
            self.logo_state.set_from_stock(gtk.STOCK_NO, 1)
            self.running = False
        
    def stop(self):
        try:
            gobject.source_remove(self.timer)
            print "matando proceso %d" % self.pid
            os.kill(self.pid, signal.SIGTERM)
        except: pass
        if self.config["autodetect"]: self.config["device"] = ""
        self.logo_state.set_from_stock(gtk.STOCK_NO, 1)

    # the __init__ method
    def __init__(self,applet,iid):

        # do it a gobject.
        self.__gobject_init__()

        
        self.running = False
        self.tooltip_text = ""

        self.orientation = gnomeapplet.ORIENT_DOWN
       
        self.propxml="""
        <popup name="button3">
        <menuitem name="Item 1" verb="Props" label="_Preferencias" pixtype="stock" pixname="gtk-properties"/>
        <menuitem name="Item 2" verb="About" label="_Acerca de" pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
        """

        self.verbs = [ ( "Props", self.properties ),
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

        # update info from filesystem
        #gtk.timeout_add(self.timeout_interval,self.timeout_callback, self)
        #
        # connect some signals to the applet
        self.applet.connect("button-press-event",self.applet_press)
        self.applet.connect("change-orient",self.change_orientation)
        self.applet.connect("delete-event",self.cleanup)

        self.game_controllers = ("joystick","joypad","wiimote")
        self.config = { "autostart":False, \
                        "autodetect":True, \
                        "type":self.game_controllers[1], \
                        "device":""
                      }
        self.gconfkey = '/apps/joy_applet/'
        self.prefs = gconf_prefs.AutoPrefs(self.gconfkey, self.config)
        self.config = self.prefs.gconf_load()
        if self.prefs.first_run:
            self.prefs.gconf_save() 
        self.path = {"joymouse":"/usr/bin/joymouse", "wminput":"/usr/local/bin/wminput"}
        

        # create especific widgets
        self.logo_pixbuf = gtk.gdk.pixbuf_new_from_file(joystick_image)
        self.status_logo = gtk.Image()
        image = gtk.Image()
        image.set_from_pixbuf(self.logo_pixbuf)
        self.box.pack_start(image)
        self.logo_state = gtk.Image()
        self.logo_state.set_from_stock(gtk.STOCK_NO, 1)
        self.box.pack_start(self.logo_state)

        #self.b = gtk.Label(_("Control por joystick"))
        #self.box.pack_start(self.b)
        if self.config["autostart"]:
            self.run()
            self.running = True
        self.applet.show_all()


gobject.type_register(joyApplet)

# bonobo factory of baseApplets
def joy_applet_factory(applet, iid):
    joyApplet(applet,iid)
    return gtk.TRUE

# run it in a gtk window
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Debugger mode")
    main_window.set_decorated(False)
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    joy_applet_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:GNOME_JoymouseApplet_Factory",
                                joyApplet.__gtype__,
                                "hello", "0", joy_applet_factory)
