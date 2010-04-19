# -*- coding: utf-8 -*-

import gconf_prefs
import os
from tempfile import mkdtemp
import gettext

name = "COMPI"
version = "0.4.2"
host = "localhost"
festival_port = 1314
base = None
player = None
mouse_tools = os.path.exists("/usr/lib/python2.5/site-packages/mouse.py")
temp_dir = mkdtemp('compi')
# Recopilacion de las voces instaladas para festival
available_lang = {}
for l in os.listdir('/usr/share/festival/voices'):
    i = 1
    for d in os.listdir(os.path.join('/usr/share/festival/voices',l)):
        available_lang["%s_%d" %(l, i)] = "voice_%s" % d
        i += 1
        
# Multi-lingual support
_ = gettext.lgettext
gettext.textdomain("compi")
gettext.bindtextdomain("compi", "/usr/share/compi/compi%s/translations" % version.replace('.',''))


default_config = {"filas":3, \
    "columnas":3, \
    "espaciado":5, \
    "tipo_letra":"Sans", \
    "home":"", \
    "color_letra":"#000000", \
    "size_letra":8, \
    "color_fondo":"#FFFFFF", \
    "size_imagen":2, \
    "resolucion_maxima":512,\
    "home":"", \
    "im_dir": os.path.expanduser('~'), \
    "aud_dir": os.path.expanduser('~'), \
    "save_dir": os.path.expanduser('~'), \
    "mos_dir": os.path.expanduser('~'), \
    "use_zlib":False, \
    "level_zlib":6, \
    "idioma":"spanish_1", \
    "sender_email":"", \
    "usuario":"", \
    "password":"", \
    "smtpserver":"", \
    "tls": False, \
    "encabezado":"Mensaje desde COMPI", \
    "remember_session": True, \
    "eco":False, \
    "selfcleaner": False, \
    "selfspace": True
    }
    
default_session = {"show_toolbar":True, \
                   "show_out":True, \
                   "show_mosaico":True, \
                   "show_text":True, \
                   "fullscreen": False, \
                   "volume":75, \
                   "opened": ""
    }
    
    
ui = "<ui> \
       <menubar name=\"MenuBar\"> \
         <menu name=\"Archivo\" action=\"File\"> \
            <menuitem name=\""+_("Nuevo")+"\" action=\"New\"/> \
            <menuitem name=\""+_("Abrir")+"\" action=\"Open\"/> \
            <menuitem name=\""+_("Guardar")+"\" action=\"Save\"/> \
            <menuitem name=\""+_("Guardar como")+"\" action=\"Save as\"/> \
           <separator/> \
            <menuitem name=\""+_("Propiedades")+"\" action=\"Properties\"/> \
           <separator/> \
            <menuitem name=\""+_("Cerrar")+"\" action=\"Close\"/> \
           <separator/> \
            <menuitem name=\""+_("Salir")+"\" action=\"Quit\"/> \
         </menu> \
         <menu name=\"Editar\" action=\"Editar\"> \
            <menuitem name=\""+_("Apariencia")+"\" action=\"Format\"/> \
           <separator/> \
            <menuitem name=\""+_("Añadir fila")+"\" action=\"Add row\"/> \
            <menuitem name=\""+_("Añadir columna")+"\" action=\"Add column\"/> \
            <menuitem name=\""+_("Eliminar fila")+"\" action=\"Delete row\"/>  \
            <menuitem name=\""+_("Eliminar columna")+"\" action=\"Delete column\"/> \
           <separator/> \
            <menuitem name=\""+_("Preferencias")+"\" action=\"Preferences\"/> \
         </menu> \
         <menu name=\"Ver\" action=\"Ver\"> \
            <menuitem name=\""+_("Mensaje")+"\" action=\"Mensaje\"/> \
            <menuitem name=\""+_("Cambiar vista")+"\" action=\"Cambiar vista\"/> \
            <menuitem name=\""+_("Barra de herramientas")+"\" action=\"Barra de herramientas\"/> \
            <menuitem name=\""+_("Pantalla")+"\" action=\"Pantalla\"/> \
         </menu> \
         <menu name=\"Ayuda\" action=\"Ayuda\" > \
            <menuitem name=\""+_("Pagina Web")+"\" action=\"Pagina Web\"/> \
            <menuitem name=\""+_("Acerca de")+"\" action=\"Acerca de\"/> \
         </menu> \
       </menubar> \
       <toolbar name=\"Toolbar\"> \
            <toolitem name=\""+_("Nuevo")+"\" action=\"New\"/> \
            <toolitem name=\""+_("Abrir")+"\" action=\"Open\"/> \
            <toolitem name=\""+_("Guardar")+"\" action=\"Save\"/> \
            <toolitem name=\""+_("Guardar como")+"\" action=\"Save as\"/> \
           <separator/> \
            <toolitem name=\""+_("Añadir fila")+"\" action=\"Add row\"/> \
            <toolitem name=\""+_("Añadir columna")+"\" action=\"Add column\"/> \
            <toolitem name=\""+_("Eliminar fila")+"\" action=\"Delete row\"/> \
            <toolitem name=\""+_("Eliminar columna")+"\" action=\"Delete column\"/> \
           <separator/> \
            <toolitem name=\""+_("Propiedades")+"\" action=\"Properties\"/> \
           <separator/> \
            <toolitem name=\""+_("Cerrar")+"\" action=\"Close\"/> \
           <separator/> \
            <toolitem name=\""+_("Salir")+"\" action=\"Quit\"/> \
       </toolbar> \
       <toolbar name=\"AccionesTexto\"> \
            <toolitem name=\""+_("Vista")+"\" action=\"Vista\"/> \
           <separator/> \
            <toolitem action=\"Leer todo\"/> \
            <toolitem action=\"Leer última\"/> \
           <separator/> \
            <toolitem action=\"Borrar todo\"/> \
            <toolitem action=\"Borrar caracter\"/> \
            <toolitem action=\"Borrar palabra\"/> \
           <separator/> \
            <toolitem action=\"Print\"/> \
       </toolbar> \
       <toolbar name=\"AccionesImagenes\"> \
            <toolitem name=\""+_("Vista")+"\" action=\"Vista\"/> \
           <separator/> \
            <toolitem action=\"Leer todo\"/> \
            <toolitem action=\"Leer último\"/> \
           <separator/> \
            <toolitem action=\"Borrar todo\"/> \
            <toolitem action=\"Borrar último\"/> \
       </toolbar> \
            <toolbar name=\""+_("Acciones")+"\"> \
            <toolitem name=\""+_("Mosaico anterior")+"\" action=\"Previous\"/> \
           <separator/> \
            <toolitem name=\""+_("Inicio")+"\" action=\"Start\"/> \
            <toolitem name=\""+_("Vista")+"\" action=\"Vista\"/> \
            <toolitem name=\""+_("Silenciar")+"\" action=\"Mute\"/> \
            <toolitem name=\""+_("e-Correo")+"\" action=\"Mail\"/> \
           <separator/> \
            <toolitem name=\""+_("Mosaico siguiente")+"\" action=\"Next\"/> \
       </toolbar> \
     </ui>"
    
prefs = gconf_prefs.AutoPrefs('/apps/compi/', default_config)
global_config = prefs.gconf_load()
last = gconf_prefs.AutoPrefs('/apps/compi/last_session/', default_session)
last_session = last.gconf_load()
if prefs.first_run:
    prefs.gconf_save()
    last.gconf_save()

def get_voice(lang = None):
    v = None
    try:
        if not lang:
            lang = global_config["idioma"]
        v = available_lang[lang]
    except:
        print "Idioma no disponible"
    return v
