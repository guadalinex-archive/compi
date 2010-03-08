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
name = "Saltos de ratón"
version = "0.1"
jump_image="/usr/share/icons/gnome/48x48/apps/launcher-program.png"
puntero = mouse.Mouse()



class jumpApplet(gnomeapplet.Applet):

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
        
    def change_orientation(self,arg1,data):
        self.orientation = self.applet.get_orient()

        if self.orientation == gnomeapplet.ORIENT_UP or self.orientation == gnomeapplet.ORIENT_DOWN:
            tmpbox = gtk.HBox()
        else:
            tmpbox = gtk.VBox()

        # reparent all the hboxes to the new tmpbox
        pass
        self.applet.show_all()

    # this callback is to create the context menu
    def applet_press(self,widget,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.create_menu()
         #if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            #if self.running:
            #    self.stop()
            #else:
            #    self.run()
            #self.running = not self.running

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
        
        check_autostart = gtk.CheckButton(label=_("Iniciar automáticamente"))
        check_autostart.set_active(self.config["autostart"])
        
        
        preferences.vbox.pack_start(gtk.Label(_("Configuración del programa")), True, True, 5)
       
        h2 = gtk.HBox()
        
        h2.pack_start(gtk.Label(_("Intervalo entre movimientos (s)")), True, True, 0)
        h2.pack_start(espera, False, False, 3)
       
        preferences.vbox.pack_start(h2, True, True, 0)
       
        preferences.vbox.pack_start(check_autostart)
        
        preferences.show_all()
        response = preferences.run()
        if response == gtk.RESPONSE_ACCEPT:
            
            self.config["espera"] = espera.get_value()
            
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
    
    def load(self, widget, event):
        filter = gtk.FileFilter()
        filter.set_name(_("Saltos"))
        filter.add_pattern("*.pos")

        title =_("Cargar posiciones")
        chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.add_filter(filter)

        chooser.set_current_folder(os.path.expanduser('~'))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            try:
                f = open(chooser.get_filename(), 'r')
                pos = eval(f.read())
                global puntero
                puntero.posiciones = pos
                f.close()
            except:
                print "Fallo al leer el fichero"
                f.close()
        chooser.destroy()
        
    def save(self, widget, event):
        filter = gtk.FileFilter()
        filter.set_name(_("Saltos"))
        filter.add_pattern("*.pos")
        title =_("Guardar posiciones")
        chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.add_filter(filter)
        chooser.set_current_folder(os.path.expanduser('~'))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            selected = chooser.get_filename()
            if not selected.endswith(".pos"):
                    selected += ".pos"
            r = gtk.RESPONSE_OK
            if os.path.exists(selected):
                aviso = gtk.Dialog(_('Aviso de sobrescritura'),
                 self.window, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_SAVE, gtk.RESPONSE_OK , gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
                aviso.vbox.pack_start(gtk.Label(_("¿Desea sobreescribir el arhcivo existente? ")), True, True, 30)
                aviso.show_all()
                r = aviso.run()
                aviso.destroy()
            if r == gtk.RESPONSE_OK:
                try:
                    f = open(selected, 'w')
                    global puntero
                    f.write(str(puntero.posiciones))
                    f.close()
                except:
                    print "Fallo al leer el fichero"
                    f.close()
        chooser.destroy()
    
    def run(self, widget):
        global puntero
        if widget.get_stock_id() == gtk.STOCK_MEDIA_RECORD:
            self.record.set_stock_id(gtk.STOCK_MEDIA_STOP)
            aviso = gtk.Dialog("Aviso", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            aviso.vbox.pack_start(gtk.Label( "Haga clic con el boton izquierdo para recordar la posición."))
            aviso.vbox.pack_start(gtk.Label( "Haga clic con el boton derecho para detener la grabación."))
            aviso.show_all()
            response = aviso.run()
            aviso.destroy()
            puntero.set_action("record")
        elif widget.get_stock_id() == gtk.STOCK_MEDIA_STOP :
            puntero.set_action("pause")
            puntero.ungrab_pointer()
            self.record.set_stock_id(gtk.STOCK_MEDIA_RECORD)
        elif widget.get_stock_id() == gtk.STOCK_MEDIA_PLAY:
            if not puntero.posiciones: # abrir posiciones ya almacenadas
                self.load(None, None)
            else:
                widget.set_stock_id(gtk.STOCK_MEDIA_PAUSE)
                puntero.set_time_wait(self.config["espera"])
                puntero.set_action("jump")
                self.running = True
        elif widget.get_stock_id() == gtk.STOCK_MEDIA_PAUSE:
            puntero.set_action("pause")
            widget.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            self.running = False

    # the __init__ method
    def __init__(self,applet,iid):

        # do it a gobject.
        self.__gobject_init__()
        
        self.running = False
         # config values
        self.config={
        "espera" :1.0, \
        "autostart" :  False     
        }
        self.gconfkey = '/apps/jump_applet/'
        self.prefs = gconf_prefs.AutoPrefs(self.gconfkey, self.config)
        self.config = self.prefs.gconf_load()
        if self.prefs.first_run:
            self.prefs.gconf_save() 

        self.tooltip_text = ""

        self.orientation = gnomeapplet.ORIENT_DOWN
        
        self.propxml="""
        <popup name="button3">
        <menuitem name="Item 1" verb="Open" label="_Cargar..." pixtype="stock" pixname="gnome-stock-open"/>
        <menuitem name="Item 2" verb="Save" label="_Guardar..." pixtype="stock" pixname="gnome-stock-save"/>
        <menuitem name="Item 3" verb="Props" label="_Preferencias" pixtype="stock" pixname="gtk-properties"/>
        <menuitem name="Item 4" verb="About" label="_Acerca de" pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
        """

        self.verbs = [  ( "Open", self.load ),
                        ( "Save", self.save ),
                        ( "Props", self.properties ),
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
        self.logo_pixbuf = gtk.gdk.pixbuf_new_from_file(jump_image)
        image = gtk.Image()
        image.set_from_pixbuf(self.logo_pixbuf)
        self.box.pack_start(image)
        #self.tittle = gtk.Label(name)
        self.play = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        self.record = gtk.ToolButton(gtk.STOCK_MEDIA_RECORD)
        
        # add widgets
        #self.box.pack_start(self.tittle)
        self.box.pack_start(self.play)
        self.box.pack_start(self.record)
        
        # connect some signals to the applet/widgets
        self.applet.connect("button-press-event",self.applet_press)
        self.applet.connect("change-orient",self.change_orientation)
        self.applet.connect("delete-event",self.cleanup)
        self.play.connect("clicked",self.run)
        self.record.connect("clicked",self.run)
        

        
        if self.config["autostart"]:
            self.run()
            self.running = True
        self.applet.show_all()


gobject.type_register(jumpApplet)

# bonobo factory of baseApplets
def jump_applet_factory(applet, iid):
    global puntero
    puntero.set_action("pause")
    puntero.start()
    jumpApplet(applet,iid)
    return gtk.TRUE

# run it in a gtk window
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Debugger mode")
    main_window.set_decorated(False)
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    jump_applet_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:GNOME_JumpApplet_Factory",
                                jumpApplet.__gtype__,
                                "hello", "0", jump_applet_factory)
 


