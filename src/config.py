# -*- coding: utf-8 -*-

import gconf_prefs
import os
from tempfile import mkdtemp
import gettext

# Multi-lingual support
_ = gettext.gettext
gettext.textdomain("compi")
gettext.bindtextdomain("compi", "./translations")

gui = None
player = None

mouse_tools = os.path.exists("/usr/lib/python2.5/site-packages/mouse.py")
temp_dir = mkdtemp('compi')
# Recopilacion de las voces instaladas para festival
available_lang = ["Spanish",]

default_config = {"filas":3, \
    "columnas":3, \
    "espaciado":5, \
    "tipo_letra":"Sans", \
    "color_letra":"#000000", \
    "size_letra":8, \
    "color_fondo":"#FFFFFF", \
    "size_imagen":2, \
    "resolucion_maxima":512,\
    "im_dir": os.path.expanduser('~'), \
    "aud_dir": os.path.expanduser('~'), \
    "save_dir": os.path.expanduser('~'), \
    "mos_dir": os.path.expanduser('~'), \
    "use_zlib":False, \
    "level_zlib":6, \
    "idioma":"Spanish", \
    "sender_email":"", \
    "usuario":"", \
    "password":"", \
    "smtpserver":"", \
    "tls": False, \
    "encabezado":"Mensaje desde COMPI", \
    }
    
ui = '''<ui>
            <menubar name="MenuBar">
            <menu name="Archivo" action="File">
            <menuitem name="Nuevo" action="New"/>
            <menuitem name="Abrir" action="Open"/>
            <menuitem name="Guardar" action="Save"/>
            <menuitem name="Guardar como" action="Save as"/>
            <separator/>
            <menuitem name="Imprimir" action="Print"/>
            <menuitem name="Propiedades" action="Properties"/>
            <separator/>
            <menuitem name="Cerrar" action="Close"/>
            <separator/>
            <menuitem name="Salir" action="Quit"/>
            </menu>
            <menu name="Editar" action="Editar">
            <menuitem name="Apariencia" action="Format"/>
            <separator/>
            <menuitem name="Añadir fila" action="Add row"/>
            <menuitem name="Añadir columna" action="Add column"/>
            <menuitem name="Eliminar fila" action="Delete row"/>
            <menuitem name="Eliminar columna" action="Delete column"/>
            <separator/>
            <menuitem name="Preferencias" action="Preferences"/>
            </menu>
            <menu name="Ver" action="Ver">
            <menuitem action="Mensaje"/>
            <menuitem action="Barra de herramientas"/>
            <menuitem action="Pantalla"/>
            </menu>
            <menu name="Ayuda" action="Ayuda" >
            <menuitem action="Pagina Web"/>
            <menuitem action="Acerca de"/>
            </menu>
            </menubar>
            <toolbar name="Toolbar">
            <toolitem name="Nuevo" action="New"/>
            <toolitem name="Abrir" action="Open"/>
            <toolitem name="Guardar" action="Save"/>
            <toolitem name="Guardar como" action="Save as"/>
            <separator/>
            <toolitem name="Añadir fila" action="Add row"/>
            <toolitem name="Añadir columna" action="Add column"/>
            <toolitem name="Eliminar fila" action="Delete row"/>
            <toolitem name="Eliminar columna" action="Delete column"/>
            <separator/>
            <toolitem name="Propiedades" action="Properties"/>
            <separator/>
            <toolitem name="Cerrar" action="Close"/>
            <separator/>
            <toolitem name="Salir" action="Quit"/>
            </toolbar>
            <toolbar name="AccionesTexto">
            <toolitem name="Vista" action="Vista"/>
            <separator/>
            <toolitem action="Leer todo"/>
            <toolitem action="Leer última"/>
            <separator/>
            <toolitem action="Borrar todo"/>
            <toolitem action="Borrar caracter"/>
            <toolitem action="Borrar palabra"/>
            <separator/>
            <toolitem action="Print"/>
            </toolbar>
            <toolbar name="AccionesImagenes">
            <toolitem name="Vista" action="Vista"/>
            <separator/>
            <toolitem action="Leer todo"/>
            <toolitem action="Leer último"/>
            <separator/>
            <toolitem action="Borrar todo"/>
            <toolitem action="Borrar último"/>
            </toolbar>
            <toolbar name="Acciones">
            <toolitem name="Mosaico anterior" action="Previous"/>
            <separator/>
            <toolitem name="Inicio" action="Start"/>
            <toolitem name="Vista" action="Vista"/>
            <toolitem name="Silenciar" action="Mute"/>
            <toolitem name="e-Correo" action="Mail"/>
            <separator/>
            <toolitem name="Mosaico siguiente" action="Next"/>
            </toolbar>
            </ui>'''
    
prefs = gconf_prefs.AutoPrefs('/apps/compi/', default_config)
global_config = prefs.gconf_load()
if prefs.first_run:
    prefs.gconf_save()
