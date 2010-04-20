#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
gtk.gdk.threads_init()
import gobject
import time
import os
import gconf_prefs
import config
import pango
import ossaudiodev
from threading import Timer


from mos import Mosaico
from compi_conf import Opciones
from player import Player
from shutil import rmtree


# Multi-lingual support
_ = config._
 
idioma_preferido = "spanish_1"

# Globals
name = config.name
version = config.version
host = config.host
festival_port = config.festival_port




def aviso(msg, timeout = None):
    """
    Función auxiliar para mostrar mensajes de aviso
    """
    aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
         (gtk.STOCK_OK, gtk.RESPONSE_CLOSE))
    mensaje = gtk.Label(msg)
    mensaje.set_line_wrap(True)
    mensaje.set_max_width_chars(80)
    logoad = gtk.Image()
    iconad = aviso.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
    aviso.set_icon(iconad)
    aviso.vbox.pack_start(mensaje, True, True, 50)
    aviso.show_all()
    if timeout:
        t = Timer(timeout, aviso.destroy)
        t.start()
    aviso.run()
    aviso.destroy()


class Base:
    """
    Clase principal del programa
    """

    def __init__(self):
        """
        Constructor de la clase
        """
        # Read default config from gconf
        default_config = config.global_config
        if default_config["remember_session"]:
            self.session = config.last_session
        else:
            self.session = config.default_session
        #print default_config
        
        # Create the window
        self.window = gtk.Window()
        self.window.set_icon_from_file("/usr/share/pixmaps/mosaico.png")
        self.window.set_title(name + " " + version)
        self.window.set_default_size(800,432)
        self.window.set_border_width(1)
        #self.window.move(50,50)
        self.window.connect("delete_event", self.salir)
        

        # Create a UIManager instance
        uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('UIManageExample')
        self.actiongroup = actiongroup

        # Create a ToggleAction, etc.
        actiongroup.add_toggle_actions([('Mute', gtk.STOCK_STOP, _('Silenciar'), None,
                        _('Silenciar sonido'), self.mute),
                        ('Pantalla',None,_('Pantalla completa'), '<Control>f', '', self.pantalla_completa)])

        # Create actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, _('Salir'), None,
                    'Cerrar el programa', self.salir),
                    
                    ('File', None, _('_Archivo')),
                    
                    ('New', gtk.STOCK_NEW, _('Nuevo'), None,
                    _('Crear un nuevo mosaico'), self.nuevo_mosaico),
                    
                    ('Open', gtk.STOCK_OPEN, _('Abrir'), None, 
                    _('Abrir un mosaico'), self.abrir),
                    
                    ('Save', gtk.STOCK_SAVE, _('Guardar'), None, 
                    _('Guardar los cambios del mosaico actual'), self.guardar),
                    
                    ('Save as', gtk.STOCK_SAVE_AS, _('Guardar como'), None, 
                    _('Guardar el mosaico actual'), self.guardar_como),
                    
                    ('Print', None, _('Imprimir')),
                    
                    ('Properties', gtk.STOCK_PROPERTIES, _('Propiedades'), 
                    None, '', self.properties),
                    
                    ('Preferences', gtk.STOCK_PREFERENCES, _('Opciones'), 
                    None, '', self.preferences),
                    
                    ('Close', gtk.STOCK_CLOSE, _('Cerrar'), None,
                    _('Cerrar mosaico actual'), self.cerrar_mosaico),
                    
                    ('Format', None, _('Formato'), None, '', self.format),
                    
                    ('Add row', gtk.STOCK_ADD, _('Insertar fila'),None,
                    _('Insertar una fila'), self.insertar_fila),
                    
                    ('Add column', gtk.STOCK_ADD, _('Insertar columna'),None,
                    _('Insertar una columna'), self.insertar_columna),
                    
                    ('Delete row', gtk.STOCK_REMOVE, _('Eliminar fila'),None,
                    _('Eliminar la última fila'), self.eliminar_fila),
                    
                    ('Delete column', gtk.STOCK_REMOVE, _('Eliminar columna'),None,
                    _('Eliminar la última columna'), self.eliminar_columna),
                    
                    ('Mensaje', None, _('Mensaje'),None,
                    _('Visualizar el area de mensajes'), self.mostrar_out),
                    
                    ('Barra de herramientas', None, _('Barra de herramientas'),None,
                    _('Visualizar la barra de herramientas'), self.mostrar_toolbar),
                    
                    ('Cambiar vista', None, _('Cambiar vista'),None,
                    _(u'Intercambiar modo texto/gráfico'), self.cambiar_vista),
                    
                    ('Herramientas',None,_('Herramientas')),
                    
                    ('Vista', gtk.STOCK_REFRESH, _('Cambiar _modo'), 
                    '<Control>m', _('Cambia entre los modos texto e imagen')
                    , self.cambiar_vista),
                    
                    ('Leer todo', None, _('Leer _todo'), None, 
                    _('Leer el mensaje generado'), self.leer_todo),
                    
                    ('Leer última', None, _('Leer _ultima'), None, 
                    _('Leer ultima palabra escrita'), self.leer_ultima),
                    
                    ('Leer último', None, _('Leer _ultimo'), None, 
                    _('Leer el ultimo pulsado'), self.leer_ultimo),
                    
                    ('Borrar todo', None, _('Borrar todo'),None,
                    '', self.borrar_todo),
                    
                    ('Borrar caracter', None, _('Borrar caracter'),None,
                    '', self.borrar_caracter),
                    
                    ('Borrar palabra', None, _('Borrar palabra'),None,
                    '', self.borrar_palabra),
                    
                    ('Borrar último', None, _('Borrar _ultimo'),None,
                    '', self.borrar_ultimo),
                    
                    ('Previous', gtk.STOCK_GO_BACK, _('Mosaico anterior'),None,
                    _('Ir al mosaico anterior'), self.previous),
                    
                    ('Mail', gtk.STOCK_NETWORK, _('Enviar correo'),None,
                    _('Enviar mensaje por correo electrónico'), self.select_contact),
                    
                    ('Next', gtk.STOCK_GO_FORWARD, _('Mosaico siguiente'),None,
                    _('Ir al siguiente mosaico'), self.next),
                    
                    ('Start', gtk.STOCK_HOME, _('Ir al Inicio'),None,
                    _('Ir al inicio'), self.start),
                    
                    ('Ver', None, _('_Ver')),
                    
                    ('Ayuda', None, _('A_yuda')),
                    
                    ('Editar', None, _('_Editar')),
                    
                    ('Pagina Web', None, _('Pagina Web')),
                    
                    ('Acerca de', gtk.STOCK_ABOUT, _('Acerca de')
                    ,None, _('Información del programa'), self.about)])

        uimanager.insert_action_group(actiongroup, 0)

        # Add a UI description
        uimanager.add_ui_from_string(config.ui)

        # Create a MenuBar
        self.menubar = uimanager.get_widget('/MenuBar')
        # Create a Toolbar
        self.toolbar = uimanager.get_widget('/Toolbar')
        #self.acciones1 = uimanager.get_widget('/AccionesTexto')
        #self.acciones2 = uimanager.get_widget('/AccionesImagenes')
        # Create navigationbar
        #self.navbar = uimanager.get_widget('/Acciones')

        # Create area for mosaics
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.set_scrollable(True)

        # Create buttons
        do = gtk.Button(_("Leer todo"), gtk.STOCK_MEDIA_PLAY)
        do.connect("clicked", self.leer_todo)
        remove = gtk.Button(_("Borrar último"), gtk.STOCK_REMOVE)
        remove.connect("clicked", self.borrar)
        clean = gtk.Button(_("Limpiar"), gtk.STOCK_DELETE)
        clean.connect("clicked", self.borrar_todo)
        #vol = gtk.VolumeButton()
        #vol.set_value(self.session["volume"]/100.0)
        #vol.connect("popup", self.read_vol)
        #vol.connect("value-changed", self.set_volume)

        # Create area for messages (text mode)
        self.tv = gtk.TextView()
        self.tv.set_editable(True)
        self.tv.get_cursor_visible()
        font_desc = pango.FontDescription("%s %d" % (default_config["tipo_letra"], default_config["size_letra"]*2))
        self.tv.modify_font(font_desc)
        sw = gtk.ScrolledWindow()
        sw.set_size_request(300, 80)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.tv)
        self.salida1 = gtk.Frame(_("Modo texto"))
        self.salida1.add(sw)
        self.out = {}
        self.out["texto"] = self.tv.get_buffer()
        self.out["imagenes"] = []
        config.out = self.out #readable through other classes

        # Create area for messages (graphical mode)
        self.layout = gtk.Layout()
        self.out["layout"] = self.layout
        self.layout.set_size(580, 1000)
        self.sw2 = gtk.ScrolledWindow()
        self.sw2.set_size_request(300, 80)
        self.sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw2.add(self.layout)
        self.salida2 = gtk.Frame(_(u"Modo gráfico"))
        self.salida2.add(self.sw2)

        # General Box for all the widgets
        self.contenedor = gtk.VBox(False,0)
        self.outbox = gtk.HBox(False,1)
        self.delbox = gtk.VBox(False,1)
        self.contenedor.pack_start(self.menubar,False, False,0)
        self.contenedor.pack_start(self.toolbar,False,False,0)
        self.contenedor.pack_start(self.notebook,True, True,5)
        #self.contenedor.pack_start(self.navbar,False, True,2)
        self.delbox.pack_start(remove, False, False,1)
        self.delbox.pack_start(clean, False, False,1)
        #self.delbox.pack_start(vol, False, False,1)
        self.outbox.pack_start(self.salida1,True, True,0)
        self.outbox.pack_start(self.salida2,True, True,0)
        self.outbox.pack_start(do, False, False,1)
        #self.outbox.pack_start(self.delbox, False, False,1)
        self.contenedor.pack_start(self.outbox,False, False,0)
        
        self.window.add(self.contenedor)

        self.window.show_all()
        
        # Apply the last session
        self.aplicar_sesion()
        voice = config.get_voice()
        if voice:
            config.player.set_voice(voice)
        
        # Open initial mosaic
        self.opened_mos = ["",]
        if default_config["home"] and os.path.exists(default_config["home"]): 
            self.abrir(None, default_config["home"])
        if self.session["opened"]:
            for m in eval(self.session["opened"]):
                if isinstance(m, str) and os.path.exists(m): self.abrir(None, m)
        
        config.base = self

    def salir(self, widget, event=None, data=None):
        """
        Cierra el programa y guarda la sesión
        """
        if config.global_config["remember_session"]:
            self.session["opened"] = str(self.opened_mos)
            last = gconf_prefs.AutoPrefs('/apps/compi/last_session/', self.session)
            print "Guardando session"
            last.gconf_save()
        gtk.main_quit()

    def pantalla_completa(self, widget):
        """
        Cambia al modo de usuario a pantalla completa
        """
        self.session["fullscreen"] = not self.session["fullscreen"]
        if self.session["fullscreen"]:
            self.toolbar.hide()
            self.menubar.hide()
            self.window.fullscreen()
        else:
            if self.session["show_toolbar"]:
                self.toolbar.show()
            self.menubar.show()
            self.window.unfullscreen()


    def nuevo_mosaico(self, widget):
        """
        Muestra el diálogo para crear un nuevo mosaico
        """
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
        """
        Crea un nuevo mosaico y lo muestra en pantalla
        """
        mos = Mosaico(self.nombre.get_text(), self.filas.get_value_as_int(),
         self.columnas.get_value_as_int())
        label = gtk.Label(mos.nombre())
        pos = self.notebook.append_page(mos,label)
        #self.opened_mos.insert(pos, mos)
        self.notebook.set_current_page(pos)
        self.nuevo.destroy()
        self.notebook.show_all()

    def insertar_fila(self, widget):
        """
        Añade una fila al mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            self.notebook.get_nth_page(x).insertar_fila()

    def insertar_columna(self, widget):
        """
        Añade una columna al mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            self.notebook.get_nth_page(x).insertar_columna()
        else:
            self.prefered_mos.insertar_columna()

    def eliminar_fila(self, widget):
        """
        Elimina la última fila del mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            self.notebook.get_nth_page(x).borrar_fila()

    def eliminar_columna(self, widget):
        """
        Elimina la última columna del mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            self.notebook.get_nth_page(x).borrar_columna()
        else:
            self.prefered_mos.borrar_columna()

    def retroceder(self):
        """
        Cierra el mosaico actual y los anteriores que enlazaban a él
        """
        x = self.notebook.get_current_page()
        #preguntar si guardar
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            padre = mos.padre
            if padre:
                self.notebook.remove_page(x)
                self.opened_mos.pop(x)
                del mos
                self.abrir(None, padre)
                self.retroceder()
            self.notebook.show_all()

    def cerrar_mosaico(self, widget):
        """
        Cierra el mosaico actual y enfoca al ancestro, si tuviera
        """
        x = self.notebook.get_current_page()
        #preguntar si guardar
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            padre = mos.padre
            self.notebook.remove_page(x)
            self.opened_mos.pop(x)
            del mos
            #if mos.padre:
            #    self.abrir(None, mos.padre)
            self.notebook.show_all()

    def aplicar_sesion(self):
        """
        Aplica los ajustes de la interfaz de la última vez que se usó
        """
        if self.session["show_toolbar"]:
            self.toolbar.show()
        else:
            self.toolbar.hide()
            
        if self.session["show_mosaico"]:
            self.notebook.show()
        else:
            self.notebook.hide()
            
        if self.session["show_text"]:
            #self.acciones1.show()
            self.salida1.show()
            #self.acciones2.hide()
            self.salida2.hide()
        else:
            #self.acciones2.show()
            self.salida2.show()
            #self.acciones1.hide()
            self.salida1.hide()
            
        if self.session["show_out"]:
            self.outbox.show()
        else:
            self.outbox.hide()
            #self.acciones1.hide()
            #self.acciones2.hide()
            
        if self.session["fullscreen"]:
            self.window.fullscreen()
            
        self.set_volume(vol = self.session["volume"])

    def mostrar_toolbar(self, widget):
        """
        Muestra/oculta la barra de herramientas
        """
        self.session["show_toolbar"] = not self.session["show_toolbar"]
        if self.session["show_toolbar"]:
            self.toolbar.show()
        else:
            self.toolbar.hide()
        
    def mostrar_mosaico(self, widget):
        """
        Muestra/oculta el área de los paneles
        """
        self.session["show_mosaico"] = not self.session["show_mosaico"]
        if self.session["show_mosaico"]:
            self.notebook.show()
        else:
            self.notebook.hide()

    def mostrar_out(self, widget):
        """
        Muestra/oculta el área de mensajes
        """
        self.session["show_out"] = not self.session["show_out"]
        if self.session["show_text"]:
            #self.acciones1.show()
            self.salida1.show()
            #self.acciones2.hide()
            self.salida2.hide()
        else:
            #self.acciones2.show()
            self.salida2.show()
            #self.acciones1.hide()
            self.salida1.hide()
            
        if self.session["show_out"]:
            self.outbox.show()
        else:
            self.outbox.hide()
            #self.acciones1.hide()
            #self.acciones2.hide()

    def cambiar_vista(self, widget):
        """
        Establece el modo de visualización de los mensajes
        """
        self.session["show_text"] = not self.session["show_text"]
        if self.session["show_text"]:
            #self.acciones1.show()
            self.salida1.show()
            #self.acciones2.hide()
            self.salida2.hide()
        else:
            #self.acciones2.show()
            self.salida2.show()
            #self.acciones1.hide()
            self.salida1.hide()

    def guardar(self, widget):
        """
        Guarda los cambios efectuados en el mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
        else:
            mos = self.prefered_mos
        #preguntar si guardar
        if mos.config["ruta_guardado"]:
            mos.guardar_mosaico()
        else:
            self.guardar_como(widget)
        if mos.config["ruta_guardado"] and not mos.config["ruta_guardado"] in self.opened_mos:
            self.opened_mos.append(mos.config["ruta_guardado"])

    def leer_todo(self, widget):
        """
        Reproduce el mensaje compuesto
        """
        #global player
        if self.session["show_text"]:
            config.player.read_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(),
             self.out["texto"].get_end_iter()))
        else:
            for p in self.out["imagenes"]:
                p.read()
                time.sleep(0.2)
        if config.global_config["selfcleaner"]:
            self.borrar_todo(None)

    def leer_ultimo(self, widget):
        """
        Reproduce el último pulsador seleccionado
        """
        if (len(self.out["imagenes"]) > 0):
            self.out["imagenes"][-1].leer()

    def leer_ultima(self, widget):
        """
        Lee la última palabra escrita
        """
        #global player
        it = self.out["texto"].get_end_iter()
        it.backward_word_starts(1)
        config.player.read_text(self.out["texto"].get_text(it, self.out["texto"].get_end_iter()))

    def borrar_palabra(self, widget):
        """
        Borra la última palabra escrita
        """
        it = self.out["texto"].get_end_iter()
        it.backward_word_starts(1)
        self.out["texto"].set_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(), it))

    def borrar_ultimo(self, widget):
        """
        Borra el último pulsador seleccionado
        """
        if len(self.out["imagenes"]):
            last = self.out["imagenes"].pop()
            self.out["layout"].move(last, 2000, 0)
        else:
            pass

    def borrar_todo(self, widget):
        """
        Limpia el área de mensajes
        """
        self.out["texto"].set_text("")
        self.out["imagenes"] = []
        self.layout = gtk.Layout()
        self.layout.set_size(600, 1000)
        self.sw2.remove(self.out["layout"])
        self.out["layout"] = self.layout
        self.sw2.add(self.layout)
        self.sw2.show_all()

    def borrar(self, widget):
        """
        Borra la última entrada del mensaje
        """
        if self.session["show_text"]:
            self.borrar_palabra(widget)
        else:
            self.borrar_ultimo(widget)

    def borrar_caracter(self, widget):
        """
        Borra el último caracter del mesnaje
        """
        self.out["texto"].set_text(self.out["texto"].get_text(self.out["texto"].get_start_iter(),
         self.out["texto"].get_end_iter())[:-1])

    def guardar_como(self, widget):
        """
        Muestra el diálogo de guardar el mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
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
                print _(u"Opción desconocida")
            chooser.destroy()

    def get_current_opened(self):
        """
        Devuelve el mosaico actual
        """
        x = self.notebook.get_current_page()
        path = None
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            path = mos.config["ruta_guardado"]
        return path
        
    def current_is_child(self):
        """
        Comprueba que el mosaico actual ha sido enlazado desde otro superior
        """
        x = self.notebook.get_current_page()
        child = False
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            child = mos.padre
        return child
        
    def properties (self, widget):
        """
        Muestra las propiedades del mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            dia = gtk.Dialog(_('Propiedades del mosaico'), self.window, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
            align = gtk.Alignment(0.5, 0.5, 0, 0)
            hbox = gtk.HBox(False, 5)
            vbox1 = gtk.VBox(True, 0)
            vbox2 = gtk.VBox(True, 0)
            vbox1.pack_start(gtk.Label(_('Nombre: ')))
            vbox1.pack_start(gtk.Label(_('Dimensiones: ')))
            vbox1.pack_start(gtk.Label(_('Espaciado: ')))
            vbox1.pack_start(gtk.Label(_(u'Fecha de creación: ')))
            vbox1.pack_start(gtk.Label(_('Ruta de guardado: ')))
            vbox1.pack_start(gtk.Label(_('Modificable: ')))
            vbox2.pack_start(gtk.Label(mos.config["nombre"]))
            vbox2.pack_start(gtk.Label(str(mos.config["filas"]) + 'x' + str(mos.config["columnas"])))
            vbox2.pack_start(gtk.Label(str(mos.config["espaciado"]) + 'px'))
            vbox2.pack_start(gtk.Label(str(mos.config["fecha_creacion"])))
            vbox2.pack_start(gtk.Label(mos.config["ruta_guardado"]))
            vbox2.pack_start(gtk.Label(str(mos.config["modificable"])))
            hbox.pack_start(vbox1)
            hbox.pack_start(vbox2)
            dia.vbox.pack_start(hbox)
            dia.show_all()
            result = dia.run()
            dia.destroy()

    def abrir(self, widget, mos = None, padre = None):
        """
        Abre el mosaico que recibe como parámetro o muestra el diálogo
        de navegación para seleccionarlo
        """
        #Filtro para mosaicos
        pos = 0
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
                m = Mosaico("", 1, 1, mos, padre)
                label = gtk.Label(m.nombre())
                if m.nombre():
                    pos = self.notebook.append_page(m,label)
                    self.opened_mos.insert(pos, mos)
            self.notebook.set_current_page(pos)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        else:
            print _(u"Opción desconocida")
        try:
            chooser.destroy()
        except:
            pass

        self.notebook.show_all()

    def mute(self, widget):
        """
        Activa/desactiva la reproducción de sonidos
        """
        self.session["muted"] = not self.session["muted"]

    def volume(self, d = 0):
        """
        Establece el volumen relativo de la salida de audio
        """
        try:
            mixer = ossaudiodev.openmixer()
            if mixer.controls() & (1 << ossaudiodev.SOUND_MIXER_VOLUME):
                vol = mixer.get(ossaudiodev.SOUND_MIXER_VOLUME)
                new_vol = [vol[0]+d,vol[1]+d]
                mixer.set(ossaudiodev.SOUND_MIXER_VOLUME, new_vol)
        except:
            print "No se pudo leer el volumen"

    def set_volume(self, widget=None, vol=75):
        """
        Establece el volumen de la salida de audio
        """
        if widget:
            vol = int(widget.get_value()*100)
            self.session["volume"] = vol
        try:
            mixer = ossaudiodev.openmixer()
            if mixer.controls() & (1 << ossaudiodev.SOUND_MIXER_VOLUME):
                mixer.set(ossaudiodev.SOUND_MIXER_VOLUME, (vol,vol))
        except:
            print "No se pudo cambiar el volumen"
            
    def read_vol(self, widget):
        """
        Devuelve el volumen de la salida de audio
        """
        try:
            mixer = ossaudiodev.openmixer()
            if mixer.controls() & (1 << ossaudiodev.SOUND_MIXER_VOLUME):
                vol = mixer.get(ossaudiodev.SOUND_MIXER_VOLUME)
                widget.set_value((vol[0]+vol[1])/200.0)
        except:
            print "No se pudo leer el volumen"

    def previous(self, widget):
        """
        retrocede al mosaico anterior
        """
        self.notebook.prev_page()

    def next(self, widget):
        """
        avanza al mosaico siguiente
        """
        self.notebook.next_page()

    def start(self, widget):
        """
        Muestra el primer mosaico
        """
        self.notebook.set_current_page(0)

    def preferences(self, widget):
        """
        Muestra las opciones de configuración del programa
        """
        Opciones()
        default_config = config.global_config
        font_desc = pango.FontDescription("%s %d" % (default_config["tipo_letra"], default_config["size_letra"]*2))
        self.tv.modify_font(font_desc)
        #
        
    def select_contact(self, widget):
        """
        Muestra el panel de contactos
        """
        contact_mos_path = os.path.join(os.path.expanduser('~'),".contactos.mos")
        if not os.path.exists(contact_mos_path):
            aviso(_(u"No se ha encontrado contactos previamente almacenados. Edite el mosaico que se abrirá a continuación y no olvide\nguardar los cambios."))
            
        mos = Mosaico("*Contactos*", 3,  3, contact_mos_path)
        label = gtk.Label(_("Contactos"))
        pos = self.notebook.append_page(mos,label)
        self.opened_mos.insert(pos, mos)
        self.notebook.set_current_page(pos)
        self.notebook.show_all()
        

    def format(self, widget):
        """
        Aplica el formato seleccionado al mosaico actual
        """
        x = self.notebook.get_current_page()
        if x >= 0:
            mos = self.notebook.get_nth_page(x)
            mos.formato(self.window)

    def about(self, widget):
        """
        Muestra la ventana de créditos del programa
        """
        dialog = gtk.AboutDialog()
        dialog.set_name(name)
        dialog.set_version(version)
        dialog.set_copyright("Copyright © 2007-2010 Junta de Andalucía")
        #dialog.set_website(self.url)
        #dialog.set_website_label(self.url)
        dialog.set_authors([
            _("Programadores") + ':',
            'Emilia Abad Sánchez <ailime@forja.guadalinex.org>',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>',
            'Javier Muñoz Díaz'
        ])
        dialog.set_artists([_(u"Diseño gráfico") + ':',
            'Emilia Abad Sánchez <ailime@forja.guadalinex.org>',
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>',
        ])
        dialog.set_translator_credits(_("English Beta Translation") + ':\n'
            'Fernando Ruiz Humanes <fruiz@forja.guadalinex.org>\n'
        )
        logo_file = os.path.abspath("/usr/share/pixmaps/mosaico.png")
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_(u"Comunicador Pictográfico de Guadalinex para personas discapacitadas"))
        dialog.run()
        dialog.destroy()

    def main(self):
        """
        Bucle principal de la interfaz
        """
        gtk.main()
 

if __name__ == "__main__":
    run_gui()
    
def run_gui():
    config.player = Player(host, festival_port)
    config.player.run_festival()
    aviso(_("Iniciando el motor de voces. Espere por favor."), 5)
    s = config.player.connect()
    if s:
        compigtk = Base()
        gobject.idle_add(config.player.read_text, _("Bienvenido al comunicador pictográfico de Guadalinex"))
        compigtk.main()
        s.close()
        config.player.stop_festival()
        print "Eliminando archivos temporales..."
        try:
            rmtree(config.temp_dir)
        except:
            print "Falló"
        else:
            print "OK"



