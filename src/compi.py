#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import time
import os
import signal
import gconf_prefs
import config

from mos import Mosaico
from compi_conf import Opciones
from player import Player
from shutil import rmtree



# Multi-lingual support
_ = config._


idioma = "spanish"

# Globals
name = "COMPI"
version = "beta 3"
host = "localhost"
festival_port = 1314

#player = config.player
#
mouse_tools = os.path.exists("/usr/lib/python2.5/site-packages/mouse.py")
applets = {'control':"OAFIID:GNOME_ControlApplet", \
           'joy':"OAFIID:GNOME_JoymouseApplet", \
           'scan':"OAFIID:GNOME_ScanApplet", \
           'jump':"OAFIID:GNOME_JumpApplet", \
          }
started_tools = {}


def aviso(msg, link = None):
    aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
         (gtk.STOCK_OK, gtk.RESPONSE_CLOSE))
    mensaje = gtk.Label(msg)
    logoad = gtk.Image()
    iconad = aviso.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
    aviso.set_icon(iconad)
    aviso.vbox.pack_start(mensaje)
    if link:
        enlace = gtk.LinkButton(link)
        aviso.vbox.pack_start(enlace)
    aviso.show_all()
    aviso.run()
    aviso.destroy()


class gui:

    def __init__(self):
        #read default config from gconf
        default_config = config.global_config
        #print default_config
        self.window = gtk.Window()
        self.window.set_title(name + " " + version)
        self.window.set_default_size(800,460)
        self.window.set_border_width(1)
        self.window.move(150,50)
        self.window.connect("delete_event", self.salir)

        self.show={"toolbar":True, "out":True, "mosaico":True, "text":True}
        self.fullscreen = False
        self.muted = False
        self.opened_mos = [None,]

        # Create a UIManager instance
        uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('UIManageExample')
        self.actiongroup = actiongroup

        # Create a ToggleAction, etc.
        actiongroup.add_toggle_actions([('Mute', gtk.STOCK_STOP, '_Silenciar', '<Control>m',
                        'Silenciar sonido', self.mute),
                        ('Pantalla',None,'_Pantalla completa', '<Control>f', '', self.pantalla_completa)])

        # Create actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Salir!', None,
                    'Quit the Program', gtk.main_quit),
                    
                    ('File', None, '_Archivo'),
                    
                    ('New', gtk.STOCK_NEW, '_Nuevo', None,
                    'Crear un nuevo mosaico', self.nuevo_mosaico),
                    
                    ('Open', gtk.STOCK_OPEN, 'Ab_rir', None, 
                    'Abrir un mosaico', self.abrir),
                    
                    ('Save', gtk.STOCK_SAVE, '_Guardar', '<Control>g', 
                    'Guardar los cambios del mosaico actual', self.guardar),
                    
                    ('Save as', gtk.STOCK_SAVE_AS, 'G_uardar como', None, 
                    'Guardar el mosaico actual', self.guardar_como),
                    
                    ('Print', None, '_Imprimir'),
                    
                    ('Properties', gtk.STOCK_PROPERTIES, '_Propiedades', 
                    None, '', self.properties),
                    
                    ('Preferences', gtk.STOCK_PREFERENCES, '_Opciones', 
                    None, '', self.preferences),
                    
                    ('Close', gtk.STOCK_CLOSE, '_Cerrar', None,
                    'Cerrar mosaico actual', self.cerrar_mosaico),
                    
                    ('Format', None, '_Formato', None, '', self.format),
                    
                    ('Add row', gtk.STOCK_ADD, 'Añadir fila',None,
                    'Insertar una fila', self.insertar_fila),
                    
                    ('Add column', gtk.STOCK_ADD, 'Añadir columna',None,
                    'Insertar una columna', self.insertar_columna),
                    
                    ('Delete row', gtk.STOCK_REMOVE, 'Eliminar fila',None,
                    'Eliminar la última fila', self.eliminar_fila),
                    
                    ('Delete column', gtk.STOCK_REMOVE, 'Eliminar columna',None,
                    'Eliminar la última columna', self.eliminar_columna),
                    
                    ('Mensaje', None, 'Mensaje',None,
                    'Visualizar el area de mensajes', self.mostrar_out),
                    
                    ('Barra de herramientas', None, 'Barra de herramientas',None,
                    'Visualizar la barra de herramientas', self.mostrar_toolbar),
                    
                    ('Herramientas',None,'_Herramientas'),
                    
                    ('Vista', gtk.STOCK_REFRESH, 'Cambiar _modo', 
                    '<Control>m', 'Cambia entre los modos texto e imagen'
                    , self.cambiar_vista),
                    
                    ('Leer todo', None, 'Leer _todo', None, 
                    'Leer el mensaje generado', self.leer_todo),
                    
                    ('Leer última', None, 'Leer _ultima', None, 
                    'Leer ultima palabra escrita', self.leer_ultima),
                    
                    ('Leer último', None, 'Leer _ultimo', None, 
                    'Leer el ultimo pulsado', self.leer_ultimo),
                    
                    ('Borrar todo', None, '_Borrar todo',None,
                    '', self.borrar_todo),
                    
                    ('Borrar caracter', None, 'Borrar ca_racter',None,
                    '', self.borrar_caracter),
                    
                    ('Borrar palabra', None, 'Borrar _palabra',None,
                    '', self.borrar_palabra),
                    
                    ('Borrar último', None, 'Borrar _ultimo',None,
                    '', self.borrar_ultimo),
                    
                    ('Previous', gtk.STOCK_GO_BACK, 'Mosaico anterior',None,
                    'Ir al mosaico anterior', self.previous),
                    
                    ('Mail', gtk.STOCK_NETWORK, 'Enviar correo',None,
                    'Enviar mensajer por correo electrónico', self.select_contact),
                    
                    ('Next', gtk.STOCK_GO_FORWARD, 'Mosaico siguiente',None,
                    'Ir al siguiente mosaico', self.next),
                    
                    ('Start', gtk.STOCK_HOME, 'Ir al Inicio',None,
                    'Ir al inicio', self.start),
                    
                    ('Ver', None, '_Ver'),
                    
                    ('Ayuda', None, 'Ay_uda'),
                    
                    ('Editar', None, '_Editar'),
                    
                    ('Pagina Web', None, '_Pagina Web'),
                    
                    ('Acerca de', gtk.STOCK_ABOUT, '_Acerca de'
                    ,None, 'Información del programa', self.about)])

        uimanager.insert_action_group(actiongroup, 0)

        # Add a UI description
        uimanager.add_ui_from_string(config.ui)

        # Create a MenuBar
        self.menubar = uimanager.get_widget('/MenuBar')
        # Create a Toolbar
        self.toolbar = uimanager.get_widget('/Toolbar')
        self.acciones1 = uimanager.get_widget('/AccionesTexto')
        self.acciones2 = uimanager.get_widget('/AccionesImagenes')
        # Create navigationbar
        self.navbar = uimanager.get_widget('/Acciones')

        # Create area for mosaics
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.set_scrollable(True)

        # Create button
        do = gtk.Button(_("Leer todo"), gtk.STOCK_MEDIA_PLAY)
        do.connect("clicked", self.leer_todo)
        remove = gtk.Button(_("Borrar último"), gtk.STOCK_REMOVE)
        remove.connect("clicked", self.borrar)
        clean = gtk.Button(_("Limpiar"), gtk.STOCK_DELETE)
        clean.connect("clicked", self.borrar_todo)

        #Create area for messages
        texto = gtk.TextView()
        texto.set_editable(True)
        texto.get_cursor_visible()
        sw = gtk.ScrolledWindow()
        sw.set_size_request(300, 120)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(texto)
        self.salida1 = gtk.Frame(_("Modo texto"))
        self.salida1.add(sw)
        self.out = {}
        self.out["texto"] = texto.get_buffer()
        self.out["imagenes"] = []
        config.out = self.out

        self.layout = gtk.Layout()
        self.out["layout"] = self.layout
        self.layout.set_size(600, 1000)
        self.sw2 = gtk.ScrolledWindow()
        self.sw2.set_size_request(300, 120)
        self.sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw2.add(self.layout)
        self.salida2 = gtk.Frame(_("Modo gráfico"))
        self.salida2.add(self.sw2)

        # Create start options
        frame = gtk.Frame()
        start = gtk.Table(3, 4 , False)
        open_button = gtk.Button(stock = gtk.STOCK_OPEN)
        new_button = gtk.Button(stock = gtk.STOCK_NEW)
        fullscreen_button = gtk.Button(stock = gtk.STOCK_FULLSCREEN)
        quit_button = gtk.Button(stock = gtk.STOCK_QUIT)
        self.barrido_button = gtk.Button(_("Barrido de\n pantalla "))
        self.saltos_button = gtk.Button(_("  Saltos \nde ratón"))
        self.joystick_button = gtk.Button(_("Control por\n   Joystick "))
        self.desplazamiento_button = gtk.Button(_("Desplazamiento"))
        self.barrido_button.set_sensitive(mouse_tools)
        self.saltos_button.set_sensitive(mouse_tools)
        self.joystick_button.set_sensitive(mouse_tools)
        self.desplazamiento_button.set_sensitive(mouse_tools)
        global applets
        self.barrido_button.connect("clicked", run_tool, applets["scan"])
        self.saltos_button.connect("clicked", run_tool, applets["jump"])
        self.joystick_button.connect("clicked", run_tool, applets["joy"])
        self.desplazamiento_button.connect("clicked", run_tool, applets["control"])
        
        # Attach in the table
        start.attach(open_button, 0, 1, 0, 1,
         gtk.SHRINK | gtk.EXPAND  |gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(new_button,1, 2, 0, 1,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(fullscreen_button, 2, 3, 0, 1,
         gtk.SHRINK | gtk.EXPAND|gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(quit_button, 3, 4, 0, 1,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)

        start.attach(self.barrido_button, 0, 1, 1, 2,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(self.saltos_button, 1, 2, 1, 2,
         gtk.SHRINK | gtk.EXPAND  |gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(self.joystick_button, 2, 3, 1, 2,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        start.attach(self.desplazamiento_button, 3, 4, 1, 2,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        
        pref_path_mos = os.path.join(os.path.expanduser("~"), ".prefered.mos")
        self.prefered_mos = Mosaico("Accesos directos", 1, 4, pref_path_mos)
        self.prefered_mos.set_label(_("Accesos rápidos a mosaicos"))
        #hbox = gtk.HBox(True,25)
        if not os.path.exists(pref_path_mos):
            i = 1
            for p in self.prefered_mos.config["tabla_botones"][0]:
                p.modificar_boton(nombre="Mosaico %d" % (i), pronunciacion=" ")
                p.imagen.set_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_DND)
                i += 1
                #hbox.pack_start(p, True, True, 5)
                #start.attach(p, i, i+1, 2, 3, gtk.SHRINK|gtk.FILL, gtk.SHRINK, 10, 10)
            #prefered_mos.add(hbox)
        start.attach(self.prefered_mos, 0, 4, 2, 3,
         gtk.SHRINK | gtk.EXPAND | gtk.FILL, gtk.SHRINK | gtk.EXPAND | gtk.FILL, 10, 10)
        frame.add(start)

        # connect to events
        open_button.connect("clicked", self.abrir)
        new_button.connect("clicked", self.nuevo_mosaico)
        fullscreen_button.connect("clicked", self.pantalla_completa)
        quit_button.connect("clicked", self.salir, None)

        label = gtk.Label(_("Inicio"))
        self.notebook.append_page(frame,label)
        frame.show_all()

        self.contenedor = gtk.VBox(False,0)
        self.outbox = gtk.HBox(False,1)
        self.delbox = gtk.VBox(False,1)
        self.contenedor.pack_start(self.menubar,False, False,0)
        self.contenedor.pack_start(self.toolbar,False,False,0)
        self.contenedor.pack_start(self.notebook,True, True,5)
        self.contenedor.pack_start(self.navbar,False, True,2)
        self.delbox.pack_start(remove, False, False,1)
        self.delbox.pack_start(clean, False, False,1)
        self.outbox.pack_start(self.salida1,True, True,0)
        self.outbox.pack_start(self.salida2,True, True,0)
        self.outbox.pack_start(do, False, False,1)
        self.outbox.pack_start(self.delbox, False, False,1)
        self.contenedor.pack_start(self.outbox,False, False,0)
        self.window.add(self.contenedor)

        self.window.show_all()
        self.salida2.hide()
        self.acciones2.hide()
        self.toolbar.hide()
        config.gui = self

    def salir(self, widget, event, data=None):
        self.window.destroy()
        gtk.main_quit()

    def pantalla_completa(self, widget):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            #self.toolbar.hide()
            self.menubar.hide()
            self.window.fullscreen()
        else:
            #self.toolbar.show()
            self.menubar.show()
            self.window.unfullscreen()


    def nuevo_mosaico(self, widget):
        #ventana de entrada de datos
        self.nuevo = gtk.Dialog(_("Nuevo Mosaico"), self.window,
         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        logoad = gtk.Image()
        iconad = self.nuevo.render_icon(gtk.STOCK_DIALOG_QUESTION, 1)
        mensaje = gtk.Label(_("Introduzca los datos del nuevo mosaico"))
        aceptar = gtk.Button(stock = gtk.STOCK_OK)
        adj = gtk.Adjustment(config.global_config["filas"], 1.0, 15.0, 1.0, 1.0, 0.0)
        labelnombre = gtk.Label(_("Nombre del mosaico: "))
        self.nombre = gtk.Entry(30)
        self.nombre.set_text(_("Nuevo mosaico"))
        labelfilas = gtk.Label(_("Filas: "))
        self.filas = gtk.SpinButton(adj, 1, 0)
        self.filas.set_wrap(True)
        adj = gtk.Adjustment(config.global_config["filas"], 1.0, 15.0, 1.0, 1.0, 0.0)
        labelcolumnas = gtk.Label(_("Columnas: "))
        self.columnas = gtk.SpinButton(adj, 1, 0)
        self.columnas.set_wrap(True)
        nuevov = gtk.VBox(False, 1)
        nuevoh1 = gtk.HBox(False, 1)
        nuevoh2 = gtk.HBox(False, 1)
        nuevoh3 = gtk.HBox(True, 1)

        # añadir
        self.nuevo.set_icon(iconad)
        self.nuevo.action_area.pack_start(nuevov, True, False, 10)
        nuevov.pack_start(nuevoh1, True, False, 10)
        nuevoh2.pack_start(labelnombre,False, False, 1)
        nuevoh2.pack_start(self.nombre,True, True, 1)
        nuevov.pack_start(nuevoh2, True, False, 1)
        nuevoh3.pack_start(labelfilas,False, False, 1)
        nuevoh3.pack_start(self.filas,False, False, 1)
        nuevoh3.pack_start(labelcolumnas,False, False, 1)
        nuevoh3.pack_start(self.columnas,False, False, 1)
        nuevoh1.pack_start(logoad, True, False, 10)
        nuevoh1.pack_start(mensaje, True, False, 10)
        nuevov.pack_start(nuevoh3, True, False, 1)
        nuevov.pack_start(aceptar, False, True, 10)
        logoad.set_from_stock(gtk.STOCK_DIALOG_QUESTION, 6)

        # eventos
        aceptar.connect("clicked", self.crear_mosaico)

        # mostrar
        self.nuevo.show_all()

    def crear_mosaico(self, widget):
        mos = Mosaico(self.nombre.get_text(), self.filas.get_value_as_int(),
         self.columnas.get_value_as_int())
        label = gtk.Label(mos.nombre())
        pos = self.notebook.append_page(mos,label)
        self.opened_mos.insert(pos, mos)
        self.nuevo.destroy()
        self.notebook.show_all()
        self.notebook.set_current_page(pos)

    def insertar_fila(self, widget):
        x = self.notebook.get_current_page()
        if x:
            self.notebook.get_nth_page(x).insertar_fila()

    def insertar_columna(self, widget):
        x = self.notebook.get_current_page()
        if x:
            self.notebook.get_nth_page(x).insertar_columna()
        else:
            self.prefered_mos.insertar_columna()

    def eliminar_fila(self, widget):
        x = self.notebook.get_current_page()
        if x:
            self.notebook.get_nth_page(x).borrar_fila()

    def eliminar_columna(self, widget):
        x = self.notebook.get_current_page()
        if x:
            self.notebook.get_nth_page(x).borrar_columna()
        else:
            self.prefered_mos.borrar_columna()

    def cerrar_mosaico(self, widget):
        x = self.notebook.get_current_page()
        #preguntar si guardar
        if x:
            self.notebook.remove_page(x)
            self.opened_mos.pop(x)
            self.notebook.show_all()

    def mostrar_toolbar(self, widget):
        self.show["toolbar"] = not self.show["toolbar"]
        if self.show["toolbar"]:
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def mostrar_mosaico(self, widget):
        self.show["mosaico"] = not self.show["mosaico"]
        if self.show["mosaico"]:
            self.notebook.show()
        else:
            self.notebook.hide()

    def mostrar_out(self, widget):
        self.show["out"] = not self.show["out"]
        if self.show["text"]:
            self.acciones1.show()
            self.salida1.show()
            self.acciones2.hide()
            self.salida2.hide()
        else:
            self.acciones2.show()
            self.salida2.show()
            self.acciones1.hide()
            self.salida1.hide()
        if self.show["out"]:
            self.outbox.show()
        else:
            self.outbox.hide()
            self.acciones1.hide()
            self.acciones2.hide()

    def cambiar_vista(self, widget):
        self.show["text"] = not self.show["text"]
        if self.show["text"]:
            self.acciones1.show()
            self.salida1.show()
            self.acciones2.hide()
            self.salida2.hide()
        else:
            self.acciones2.show()
            self.salida2.show()
            self.acciones1.hide()
            self.salida1.hide()

    def guardar(self, widget):
        x = self.notebook.get_current_page()
        if x:
            mos = self.notebook.get_nth_page(x)
        else:
            mos = self.prefered_mos
        #preguntar si guardar
        if mos.config["ruta_guardado"]:
            mos.guardar_mosaico()
        else:
            self.guardar_como(widget)
        

    def leer_todo(self, widget):
        #global player
        if self.show["text"]:
            config.player.read_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(),
             self.out["texto"].get_end_iter()))
        else:
            for p in self.out["imagenes"]:
                p.leer()
                time.sleep(0.2)

    def leer_ultimo(self, widget):
        if (len(self.out["imagenes"]) > 0):
            self.out["imagenes"][-1].leer()

    def leer_ultima(self, widget):
        #global player
        it = self.out["texto"].get_end_iter()
        it.backward_word_starts(1)
        config.player.read_text(self.out["texto"].get_text(it, self.out["texto"].get_end_iter()))

    def borrar_palabra(self, widget):
        it = self.out["texto"].get_end_iter()
        it.backward_word_starts(1)
        self.out["texto"].set_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(), it))

    def borrar_ultimo(self, widget):
        if len(self.out["imagenes"]):
            last = self.out["imagenes"].pop()
            self.out["layout"].move(last, 2000, 0)
        else:
            pass

    def borrar_todo(self, widget):
        self.out["texto"].set_text("")
        self.out["imagenes"] = []
        self.layout = gtk.Layout()
        self.layout.set_size(600, 1000)
        self.sw2.remove(self.out["layout"])
        self.out["layout"] = self.layout
        self.sw2.add(self.layout)
        self.sw2.show_all()

    def borrar(self, widget):
        if self.show["text"]:
            self.borrar_palabra(widget)
        else:
            self.borrar_ultimo(widget)

    def borrar_caracter(self, widget):
        self.out["texto"].set_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(),
         self.out["texto"].get_end_iter())[:-1])


    def guardar_como(self, widget):
        x = self.notebook.get_current_page()
        if x:
            mos = self.notebook.get_nth_page(x)
            mosfilter = gtk.FileFilter()
            mosfilter.set_name(_("Mosaicos"))
            mosfilter.add_pattern("*.mos")

            title =_("Guardar mosaico")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
            chooser.add_filter(mosfilter)
            chooser.set_current_folder(config.global_config["save_dir"])
            chooser.set_default_response(gtk.RESPONSE_OK)
            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                selected = chooser.get_filename()
                if not selected.endswith(".mos"):
                    selected += ".mos"
                mos.config["ruta_guardado"]=selected
                if os.path.exists(selected):
                    question = gtk.Dialog(_('Aviso de sobrescritura'),
                     self.window, gtk.DIALOG_DESTROY_WITH_PARENT, 
                     (gtk.STOCK_SAVE, gtk.RESPONSE_OK , gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
                    question.vbox.pack_start(gtk.Label(_("¿Desea sobreescribir el archivo existente? ")), True, True, 30)
                    question.show_all()
                    r = question.run()
                    if r == gtk.RESPONSE_OK:
                        mos.guardar_mosaico(selected)
                    question.destroy()
                else:
                    mos.guardar_mosaico()
            elif response == gtk.RESPONSE_CANCEL:
                pass
            else:
                print _("Opción desconocida")
            chooser.destroy()

    def properties (self, widget):
        x = self.notebook.get_current_page()
        if x:
            mos = self.notebook.get_nth_page(x)
            dia = gtk.Dialog(_('Propiedades del mosaico'), self.window, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
            align = gtk.Alignment(0.5, 0.5, 0, 0)
            dia.vbox.pack_start(gtk.Label(_('Nombre: ') + mos.config["nombre"]), False, False, 5)
            dia.vbox.pack_start(gtk.Label(_('Dimensiones: ') + str(mos.config["filas"]) + 'x' + str(mos.config["columnas"])), False, False, 5)
            dia.vbox.pack_start(gtk.Label(_('Espaciado: ') + str(mos.config["espaciado"]) + 'px'))
            dia.vbox.pack_start(gtk.Label(_('Fecha de creación: ') + time.strftime("%A, %d %b %Y %H:%M:%S", mos.config["fecha_creacion"])), False, False, 5)
            dia.vbox.pack_start(gtk.Label(_('Ruta de guardado: ') + mos.config["ruta_guardado"]), False, False, 5)
            dia.vbox.pack_start(gtk.Label(_('Modificable: ') + str(mos.config["modificable"])), False, False, 5)

            dia.show_all()
            result = dia.run()
            dia.destroy()


    def abrir(self, widget, mos = None):
        #Filtro para mosaicos
        if not mos: # Muestra el dialogo de navegacion de archivos
            mosfilter = gtk.FileFilter()
            mosfilter.set_name(_("Mosaicos"))
            mosfilter.add_pattern("*.mos")

            title =_("Abrir mosaico")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(mosfilter)

            chooser.set_current_folder(config.global_config["mos_dir"])
            chooser.set_default_response(gtk.RESPONSE_OK)
            response = chooser.run()
        if mos or response == gtk.RESPONSE_OK:
            mos = mos and mos or chooser.get_filename()
            if mos in self.opened_mos: # detecta si ya lo tenemos abierto
                pos = self.opened_mos.index(mos)
            else:
                m = Mosaico("", 1, 1, mos)
                label = gtk.Label(m.nombre())
                if m.nombre():
                    pos = self.notebook.append_page(m,label)
                    self.opened_mos.insert(pos, mos)
            self.notebook.set_current_page(pos)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        else:
            print _("Opción desconocida")
        try:
            chooser.destroy()
        except:
            pass

        self.notebook.show_all()

    def mute(self, widget):
        
        self.muted = not self.muted

    def previous(self, widget):
        self.notebook.prev_page()

    def next(self, widget):
        self.notebook.next_page()

    def start(self, widget):
        self.notebook.set_current_page(0)

    def preferences(self, widget):
        Opciones()
        
    def select_contact(self, widget):
        contact_mos_path = os.path.join(os.path.expanduser('~'),".contactos.mos")
        if not os.path.exists(contact_mos_path):
            aviso (_("No se ha encontrado contactos previamente almacenados.\nEdite el mosaico que se abrirá a continuación y no olvide\nguardar los cambios."))
            
        mos = Mosaico("*Contactos*", 3,  3, contact_mos_path)
        label = gtk.Label(_("Contactos"))
        pos = self.notebook.append_page(mos,label)
        self.opened_mos.insert(pos, mos)
        self.notebook.set_current_page(pos)
        self.notebook.show_all()
        

    def format(self, widget):
        x = self.notebook.get_current_page()
        if x:
            mos = self.notebook.get_nth_page(x)
            mos.formato(self.window)

    def about(self, widget):
        dialog = gtk.AboutDialog()
        dialog.set_name(name)
        dialog.set_version(version)
        dialog.set_copyright("Copyright © 2007 Fernando Ruiz")
        #dialog.set_website(self.url)
        #dialog.set_website_label(self.url)
        dialog.set_authors([
            _("Programadores") + ':',
            'Emilia Abad Sánchez <ailime@forja.guadalinex.org>\n'
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
            'Javier Muñoz Díaz <javier.munoz@cofiman.es>\n'
        ])
        dialog.set_artists([_("Diseño gráfico") + ':',
            'Emilia Abad Sánchez <ailime@forja.guadalinex.org>\n'
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
        ])
        dialog.set_translator_credits(_("Este programa aún no ha sido traducido a otros idiomas"))
        logo_file = os.path.abspath("/usr/share/pixmaps/mosaico.png")
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_("Comunicador Pictogŕafico de Guadalinex para personas discapacitadas"))
        dialog.run()
        dialog.destroy()

    def main(self):
        gtk.main()
        
def run_tool(widget, tool):
    pid = os.fork()
    if pid: # proceso padre
        global started_tools
        started_tools[tool] = pid
    else:
        try:
            os.execv("/usr/bin/panel-test-applets", ["panel-test-applets", "--iid", tool])
        except:
            pass



def main():
    global host
    global festival_port
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    config.player = Player(host, festival_port)
    pid = os.fork()
    if pid: # proceso padre
        time.sleep(2)
        started_tools["festival"] = pid
        s = config.player.connect()
        if s:
            compigtk = gui()
            gobject.idle_add(config.player.read_text, _("Bienvenido al comunicador pictográfico de Guadalinex"))
            compigtk.main()
            for pid in started_tools.values():
                try:
                    os.kill(pid, signal.SIGKILL)
                except: pass
            s.close()
            print "Eliminando archivos temporales..."
            try:
                rmtree(config.temp_dir)
            except:
                print "Falló"
            else:
                print "OK"
    else:
        config.player.run_festival()

if __name__ == "__main__":
	main()
