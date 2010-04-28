# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import base64
import gobject
import config
from PIL import Image
from random import randint
import player
from utils import aviso_temp

_ = config._

copy = None

class Pulsador (gtk.Button):
    """
    Clase que representa los botones de los paneles
    """
    
    actions={
        "read" : _(u"Leer pronunciación"), \
        "play" : _("Reproducir archivo"), \
        "close" : _("Cerrar mosaico"), \
        "exit" : _("Salir del programa"), \
        "fullscreen" : _("Pantalla completa"), \
        "goto" : _("Ir a otro mosaico"), \
        "volup" : _("Incrementar volumen"), \
        "voldown" : _("Decrementar volumen"), \
        "eraseall" : _("Borrar todo el mensaje"), \
        "eraselast" : _(u"Borrar último"), \
        "send_by_mail" : _("Enviar por e-correo"), \
    }


    def __init__(self, tipo = None, parent=None):
        """
        Constructor de la clase
        """
        gtk.Button.__init__(self)
        box = gtk.VBox(False, 0)
        box.set_border_width(2)
        self.ident = randint(1, 10**8)
        self.tipo = tipo
        if tipo == "contacto":
            self.default_image = "/usr/share/pixmaps/login-photo.png"
        else:
            self.default_image = "/usr/share/pixmaps/edit.png"
        self.player = config.player
        self.ispreview = False
        self.ismini = False
        self.ismodificable = True
        self.mosaico = parent
        
        self.default_config={
        "nombre":"", \
        "tipo_letra":config.global_config["tipo_letra"], \
        "color_letra":config.global_config["color_letra"], \
        "size_letra":config.global_config["size_letra"], \
        "color_fondo":config.global_config["color_fondo"], \
        "escalado_imagen":config.global_config["size_imagen"], \
        "pronunciacion":"", \
        "sonido":"", \
        "imagen":self.default_image, \
        "enlace_a_mosaico":"", \
        "action":"read", \
        "mail":"", \
        }
        self.config = self.default_config
        self.tooltips = gtk.Tooltip()
        self.tooltips.set_text(_("Clic izquierdo: ")+self.actions[self.config["action"]]+"\n"+_("Clic derecho: Editar pulsador")+"\n")
        self.imagen = gtk.Image()
        self.titulo = gtk.Label("")
        self.titulo.set_justify(gtk.JUSTIFY_CENTER)
        #self.titulo.set_max_width_chars(16)
        self.titulo.set_line_wrap(True)
        box.pack_start(self.imagen, True, True, 0)
        box.pack_end(self.titulo, False, False, 0)
        self.add(box)
        self.connect_object("event", self.button_press, self)
        self.aplicar_formato()
        self.show_all()


    #Metodos
    def aplicar_formato(self):
        """
        Establece el aspecto del botón
        """
        self.titulo.set_use_markup(True)
        if self.config["color_fondo"]:
            self.modify_bg(gtk.STATE_NORMAL,
            self.get_colormap().alloc_color(self.config["color_fondo"]))
        self.titulo.set_markup("<span font_desc=\"%s %d \" foreground=\"%s\">%s</span>" % (self.config["tipo_letra"], self.config["size_letra"], self.config["color_letra"], self.config["nombre"]))
        self.titulo.set_justify(gtk.JUSTIFY_CENTER)
        #self.titulo.set_max_width_chars(16)
        self.titulo.set_line_wrap(True)
        self.tooltips.set_text(_("Clic izquierdo: ")+self.actions[self.config["action"]]+"\n"+_("Clic derecho: Editar pulsador")+"\n"+_("Clic central:   Cortar y pegar"))
        if self.config["imagen"] and os.path.exists(self.config["imagen"]):
            x = self.ismini and 1 or self.config["escalado_imagen"]
            size = x*32, x*32
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.config["imagen"], size[0], size[1])
            self.imagen.set_from_pixbuf(pixbuf)
            self.show_all()
        else:
            self.imagen.clear()
            self.imagen.hide()
        
    def modificar_boton(self, nombre=None, pronunciacion=None, sonido=None, tipo_letra=None, color_letra=None, tamano_letra=None, color_fondo=None, imagen="",  enlace_a_mosaico=None, escalado=0, mail=None, action=None):
        """
        Establecelos atributos del botón
        """
        if self.ismodificable:
            self.config["nombre"] = nombre and nombre or self.config["nombre"]
            self.config["tipo_letra"] = tipo_letra and tipo_letra or self.config["tipo_letra"]
            self.config["color_letra"] = color_letra and self.tohex(color_letra)  or self.config["color_letra"]
            self.config["size_letra"] = tamano_letra and tamano_letra or self.config["size_letra"]
            self.config["color_fondo"] =  color_fondo and self.tohex(color_fondo) or self.config["color_fondo"]
            self.config["pronunciacion"] = pronunciacion and pronunciacion or self.config["pronunciacion"]
            self.config["sonido"] = sonido and sonido or self.config["sonido"]
            self.config["mail"] = mail and mail or self.config["mail"]
            self.config["action"] = action and action or self.config["action"]
            self.config["imagen"] = imagen #and imagen or self.config["imagen"]
            self.config["escalado_imagen"] = escalado and escalado or self.config["escalado_imagen"]
            self.config["enlace_a_mosaico"] = enlace_a_mosaico and enlace_a_mosaico or self.config["enlace_a_mosaico"]
            self.aplicar_formato()

    def limpiar_boton(self):
        """
        Restaura la configuración por defecto
        """
        self.config = self.default_config
        self.aplicar_formato()

    def from_string(self, ident, s):
        """
        Lee la 
        """
        path = config.temp_dir
        self.ident = ident
        for k, v in s.iteritems():
            if k == "imagen":
                if v:
                    try:
                        file = str(os.path.join(path, v["file"]))
                        f = open(file,"w")
                        f.write(base64.b64decode(v["data"]))
                        f.close()
                        self.config["imagen"] = file
                    except:
                        print "Fallo al recuperar la imagen"
                        self.config["imagen"] = ""
                else:
                     self.config["imagen"] = ""
            elif k == "sonido" and v:
                try:
                    file = str(os.path.join(path, v["file"]))
                    f = open(file,"w")
                    f.write(base64.b64decode(v["data"]))
                    f.close()
                    self.config["sonido"] = file
                except:
                    print "Fallo al recuperar el sonido"
                    self.config["sonido"] = ""
            elif k == "fila":
                i = int(v)
            elif k == "columna":
                j = int(v)
            elif k == "size_letra" or k == "escalado_imagen":
                self.config[str(k)] = int(v)
            else:
                self.config[str(k)] = str(v)
        self.aplicar_formato()
        return i, j

    def lock(self):
        self.ismodificable=False

    def unlock(self):
        self.ismodificable=True

    def tohex(self, rgb):
        zero = "0000"
        red = (zero+hex(rgb[0]/256)[2:])[-2:]
        green = (zero+hex(rgb[1]/256)[2:])[-2:]
        blue = (zero+hex(rgb[2]/256)[2:])[-2:]
        return "#%s%s%s" % (red, green, blue)

    def to_string(self, i = -1, j = -1):
        tab = "\t\t"
        r = tab + "<Pulsador_%s>\n" % (self.ident)
        #r += tab + "\t<ident>%s</ident>\n" % (self.ident)
        r += tab + "\t<fila>%d</fila>\n" % i
        r += tab + "\t<columna>%d</columna>\n" % j
        p = ""

        compress = config.global_config["use_zlib"]
       
        for k, v in self.config.iteritems():
            if k == "sonido" and v:
                # convertir sonido v a texto
                try:
                    audio = open(v, "r")
                    f = os.path.split(v)[1]
                    if compress:
                        b64 = zlib.compress(base64.b64encode(audio.read()),
                         config.global_config["level_zlib"])
                    else:
                        b64 = base64.b64encode(audio.read())
                    audio.close()
                    p += tab + "\t<%s>\n" % k
                    p += tab + "\t\t<file>%s</file>\n" % f
                    p += tab + "\t\t<coding>%s</coding>\n" % "base64"
                    p += tab + "\t\t<zlib-compressed>%s</zlib-compressed>\n" % compress
                    p += tab + "\t\t<data>%s</data>\n" % b64
                    p += tab + "\t</%s>\n" % k
                except:
                    pass
                    
            elif k == "imagen" and v != self.default_image:
                # convertir imagen v a texto
                try:
                    picture = open(v, "r")
                    f = os.path.split(v)[1]
                    if compress:
                        b64 = zlib.compress(base64.b64encode(picture.read()),
                         config.global_config["level_zlib"])
                    else:
                        b64 = base64.b64encode(picture.read())
                    picture.close()
                    p += tab + "\t<%s>\n" % k
                    p += tab + "\t\t<file>%s</file>\n" % f
                    p += tab + "\t\t<coding>%s</coding>\n" % "base64"
                    p += tab + "\t\t<zlib-compressed>%s</zlib-compressed>\n" % compress
                    p += tab + "\t\t<data>%s</data>\n" % b64
                    p += tab + "\t</%s>\n" % k 
                except:
                    r += tab + "\t<%s>%s</%s>\n" % (k, v , k)
                    
            else:
                r += tab + "\t<%s>%s</%s>\n" % (k, v , k)
        r += p + tab + "</Pulsador_%s>\n" % (self.ident)
        return r

    def button_press(self, widget, event):
        # global base
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button==1:
                if not self.tipo == "contacto" and self.config["imagen"] == self.default_image:
                    self.edit(None)
                else:
                    eval("self.%s()" % widget.config["action"])
            elif event.button==3:
                #print "Click con el botón derecho"
                if widget.ismodificable and not widget.ispreview and not config.base.session["fullscreen"]:
                    #print "Editar Pulsador"
                    # mostrar ventana edición
                    contextmenu = gtk.Menu()
                    editar = gtk.MenuItem(_("Editar"))
                    copiar = gtk.MenuItem(_("Copiar"))
                    pegar = gtk.MenuItem(_("Pegar"))
                    mover = gtk.MenuItem(_("Mover"))
                    limpiar = gtk.MenuItem(_("Limpiar"))
                    
                    editar.connect("activate", self.edit)
                    limpiar.connect("activate", self.clean)
                    copiar.connect("activate", self.copy)
                    pegar.connect("activate", self.paste)
                    mover.connect("activate", self.move)
                    
                    contextmenu.append(editar)
                    global copy
                    contextmenu.append(copiar)
                    if copy:
                        contextmenu.append(mover)
                        contextmenu.append(pegar)
                    contextmenu.append(limpiar)
                    
                    contextmenu.show_all()
                    contextmenu.popup(None, None, None, event.button, 0)
                    
                    
                    

    def edit(self, widget):
        p = Propiedades(self)

    def clean(self, widget):
        b = Pulsador()
        self.config = b.config
        self.aplicar_formato()

    def move(self, widget):
        global copy
        if copy and copy.tipo == self.tipo:
            t = self.config
            self.config = copy.config
            copy.config = t
            self.aplicar_formato()
            copy.set_relief(gtk.RELIEF_NORMAL)
            copy.aplicar_formato()
            copy = None
        

    def copy(self, widget):
        #print "Almacenar Pulsador en memoria"
        global copy
        if copy:
            copy.set_relief(gtk.RELIEF_NORMAL)
        copy = self
        copy.set_relief(gtk.RELIEF_NONE)
              
    def paste(self, widget):
        global copy
        if copy and copy.tipo == self.tipo:
            self.config = copy.config
            self.aplicar_formato()
            copy.set_relief(gtk.RELIEF_NORMAL)
            copy = None

    def clone(self):
        b = Pulsador()
        b.config = self.config.copy()
        b.aplicar_formato()
        return b

    def preview(self):
        b = self.clone()
        b.ispreview = True
        return b

    def mini(self):
        b = self.clone()
        b.ismini = True
        b.aplicar_formato()
        b.titulo.set_markup("<span font_desc=\"%s %d \" foreground=\"%s\">%s</span>" % (self.config["tipo_letra"], 8, self.config["color_letra"], self.config["nombre"]))
        b.lock()
        b.ispreview = False
        b.set_relief(gtk.RELIEF_NONE)
        return b
                
    def read(self):
        if config.global_config["eco"] and self.config["pronunciacion"]:
            print "Leyendo el Pulsador [%s]...\t" % self.config["nombre"]
            self.player.read_text(self.config["pronunciacion"])
        if not (self.ispreview or self.ismini):
            out = config.base.out
            iter = out["texto"].get_end_iter()
            end = iter.copy()
            text = self.config["nombre"]
            mensaje = out["texto"].get_text(out["texto"].get_start_iter(),end)
            #check last character
            if config.global_config["selfspace"] and len(mensaje) > 2:
                last_char = mensaje[-2]
            elif len(mensaje) > 1:
                last_char = mensaje[-1]
            else:
                last_char  = '.'
            
            if text.startswith('.'):
                result = iter.backward_chars(1)
                out["texto"].delete(iter,end)
            elif self.config["nombre"].startswith("-"):
                result = iter.backward_chars(self.config["nombre"].count('-'))
                text = text.replace('-','')
                out["texto"].delete(iter,end)
            elif self.config["nombre"].startswith("+"):
                result = iter.backward_chars(self.config["nombre"].count('+'))
                text = text.replace('+','')
            else:
                w, h = out["layout"].get_size()
                m = self.mini()
                out["imagenes"].append(m)
                out["layout"].put(m, ((len(out["imagenes"]) - 1) * 100) % w, (((len(out["imagenes"]) - 1) * 100) / w)*100)
            #add space to the end
            if config.global_config["selfspace"] and not text.endswith(' '):
                text = text + ' '
            #capitalize if new phrase
            if last_char == '.':
                text = text.capitalize()
            #insert text
            out["texto"].insert(iter, text)
            #bach to the father
            if config.base.current_is_child():
                config.base.retroceder()
                
    def play(self):
        if self.config["sonido"]:
            print "Reproduciendo archivo de audio del Pulsador [%s]...\t" % self.config["nombre"]
            self.player.play_audio(self.config["sonido"])
        if not (self.ispreview or self.ismini):
            out = config.base.out
            w, h = out["layout"].get_size()
            out["texto"].insert(out["texto"].get_end_iter(), " #" + self.config["nombre"] + "# ")
            m = self.mini()
            out["imagenes"].append(m)
            out["layout"].put(m, ((len(out["imagenes"]) - 1) * 100) % w , (((len(out["imagenes"]) - 1) * 100) / w)*100)
            if config.base.current_is_child():
                config.base.retroceder()
                        
    def close(self):
        if not (self.ispreview or self.ismini):
            config.base.cerrar_mosaico(None)
        
    def exit(self):
        if not (self.ispreview or self.ismini):
            config.base.salir(None)
        
    def fullscreen(self):
        if not (self.ispreview or self.ismini):
            config.base.pantalla_completa(None)
    
    def goto(self):
        if not (self.ispreview or self.ismini) and self.config["enlace_a_mosaico"]:
            try:
                relative = os.path.join(os.path.dirname(self.mosaico.config["ruta_guardado"]), os.path.basename(self.config["enlace_a_mosaico"]))
            except:
                print "Error de redireccionamiento: %s" % relative
            else:
                if os.path.exists(self.config["enlace_a_mosaico"]):
                    print "Abriendo mosaico %s..." % os.path.split(self.config["enlace_a_mosaico"])[1]
                    config.base.abrir(None, self.config["enlace_a_mosaico"], config.base.get_current_opened())
                elif os.path.exists(relative):
                    print "Abriendo mosaico %s..." % os.path.split(relative)[1]
                    config.base.abrir(None, relative, config.base.get_current_opened())
                else:
                    mensaje = _("No se puede acceder al archivo ") + self.config["enlace_a_mosaico"] + _(". Revise que existe y que tiene permisos de lectura.")
                    aviso_temp(mensaje, 5)
                
    def volup(self):
        if not (self.ispreview or self.ismini):
            config.base.volume(+10)
        
    def voldown(self):
        if not (self.ispreview or self.ismini):
            config.base.volume(-10)
        
    def eraseall(self):
        if not (self.ispreview or self.ismini):
            config.base.borrar_todo(None)
        
    def eraselast(self):
        if not (self.ispreview or self.ismini):
            config.base.borrar(None)
        
    def send_by_mail(self):
        if not (self.ispreview or self.ismini):
            self.enviar_correo()

            
    def enviar_correo(self, coding = 'utf-8'):
        sender = config.global_config["sender_email"]
        user = config.global_config["usuario"]
        header = config.global_config["encabezado"]
        receiver = self.config["mail"]
        text = config.base.out["texto"].get_text(config.base.out["texto"].get_start_iter(),
                config.base.out["texto"].get_end_iter())
        password = base64.b64decode(config.global_config["password"])
        smtpserver = config.global_config["smtpserver"]
        tls = config.global_config["tls"]
        if sender and password and smtpserver:
            mensaje = _("El siguiente mensaje se enviará automáticamente en 5 segundos")
            mensaje += "\n" + _("DE:") + sender
            mensaje += "\n" + _("PARA:")+receiver
            mensaje += "\n" + _("ASUNTO:")+header
            mensaje += "\n" + text
            av = aviso_temp(mensaje, 5)
            response = av.response
            if response == gtk.RESPONSE_CLOSE:
                return 0
            else:
                import smtplib
                from email.MIMEText import MIMEText
                from email.Header import Header
                from email.Utils import formatdate
                
                body = unicode(text, 'utf-8')
                msg = MIMEText(body.encode(coding), 'plain', coding)
                msg['From']    = sender
                msg['To']      = receiver
                msg['Date'] = formatdate(localtime=1)
                msg['Subject'] = Header(header, coding)  # la 'ñ' no se puede codificar en ASCII
                
                try:
                    server = smtplib.SMTP(smtpserver)
                except:
                    print "Fallo al conectar al servidor SMTP '%s'" % smtpserver
                    return 0
                else:
                    server.set_debuglevel(1)
                    server.ehlo(sender)
                    if tls:
                        server.starttls()
                        server.ehlo(sender)
                    try:
                        server.login(user, password)
                    except:
                        print u"Fallo de autenticación"
                        return 0
                    else:
                        server.sendmail(sender, receiver, msg.as_string())
                    server.quit()
                    return 1
        else:
            aviso_temp(_(u"No ha configurado aún las opciones de correo saliente."))
            


class Propiedades:

    def __init__(self, p):
        self.pulsador_original = p
        self.pulsador = p.preview()
        self.window = gtk.Dialog(_("Propiedades del Pulsador"), None,
         gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.window.set_has_separator(True)
        
        contenedor=gtk.Table(5, 4, False)
        contenedor.set_row_spacing(3, 5)
        contenedor.set_row_spacing(4, 20)

        name=gtk.Label(_("Nombre"))
        image=gtk.Label(_("Imagen"))
        fondo=gtk.Label(_("Color de fondo"))
        texto=gtk.Label(_("Color del texto"))
        accion=gtk.Label(_(u"Acción"))
        self.campo= gtk.Label("")
        
        self.entryname = gtk.Entry()
        self.entryname.set_text(p.config["nombre"])
        self.entry = gtk.Entry()
        
       
        self.entryimage = gtk.Entry()
        if not p.config["imagen"] == p.default_image and not p.tipo == "contacto":
            self.entryimage.set_text(p.config["imagen"])
        
        liststore = gtk.ListStore(str, str)
        self.combobox = gtk.ComboBox(liststore) 
        for a, d in p.actions.iteritems():
            liststore.append([a, d])
        #action = gtk.CellRendererText()
        #self.combobox.pack_start(action, True)
        #self.combobox.add_attribute(action, 'text', 0)  
        desc = gtk.CellRendererText()
        self.combobox.pack_start(desc, True)
        self.combobox.add_attribute(desc, 'text', 1)
        i = 0
        for a in self.combobox.get_model():
            if a[0] == p.config["action"]:
                self.combobox.set_active(i)
                break
            i += 1
        self.combobox.connect("changed", self.action_changed)
        
        self.ex=gtk.Button(_("Examinar"))
        self.ex.connect("clicked", self.buscar_archivo)
        ex2=gtk.Button(_("Examinar"))
        ex2.connect("clicked", self.buscar_imagen)
        
        self.fontbutton = gtk.FontButton("%s %d" %(p.config["tipo_letra"],
         p.config["size_letra"]))
        self.fontbutton.set_use_font(True)
        self.fontbutton.set_title('Fuente')
        
        self.colorfont = gtk.ColorButton(color=p.get_colormap().alloc_color(p.config["color_letra"]))
        self.colorback = gtk.ColorButton(color=p.get_colormap().alloc_color(p.config["color_fondo"]))
        adj = gtk.Adjustment(p.config["escalado_imagen"], 1.0, 10.0, 1.0, 1.0, 0.0)
        
        self.hscale = gtk.HScale(adj)
        self.hscale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        self.hscale.set_digits(0)
        self.hscale.connect("value-changed", self.actualizar)
        
        self.entryname.connect("focus-out-event", self.actualizar)
            
        #primera columna
        contenedor.attach(self.pulsador, 0, 1, 0, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK, 10, 10)
        contenedor.attach(texto, 0, 1, 4, 5, gtk.SHRINK, gtk.SHRINK, 0, 0)

        #seguna columna
        contenedor.attach(name, 1, 2, 0, 1, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(accion, 1, 2, 1, 2, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.campo, 1, 2, 2, 3, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(image, 1, 2, 3, 4, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.colorfont, 1, 2, 4, 5, gtk.SHRINK, gtk.SHRINK, 0, 0)


        #tercera columna
        contenedor.attach(self.entryname, 2, 3, 0, 1, gtk.EXPAND|gtk.SHRINK|gtk.FILL, gtk.EXPAND|gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.combobox, 2, 4, 1, 2, gtk.EXPAND|gtk.SHRINK|gtk.FILL, gtk.EXPAND|gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.entry, 2, 3, 2, 3, gtk.EXPAND|gtk.SHRINK|gtk.FILL, gtk.EXPAND|gtk.SHRINK|gtk.FILL, 0, 0)
        #contenedor.attach(self.entryimage, 2, 3, 3, 4, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.hscale, 2, 3, 3, 4, gtk.EXPAND|gtk.SHRINK|gtk.FILL, gtk.EXPAND|gtk.SHRINK|gtk.FILL, 0, 0)
       
        contenedor.attach(fondo, 2, 3, 4, 5, gtk.SHRINK, gtk.SHRINK, 0, 0)


        #cuarta columna
        contenedor.attach(self.fontbutton, 3, 4, 0, 1, gtk.SHRINK, gtk.SHRINK, 0, 0)
        contenedor.attach(self.ex, 3, 4, 2, 3, gtk.SHRINK, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(ex2, 3, 4, 3, 4, gtk.SHRINK, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.colorback, 3, 4, 4, 5, gtk.SHRINK, gtk.SHRINK, 0, 0)

        self.window.vbox.pack_start(contenedor)
        contenedor.show_all()
        self.window.move(150,150)
        self.action_changed(None)
        response = self.window.run()

        if response == gtk.RESPONSE_ACCEPT:
                self.guardar()
        elif response == gtk.RESPONSE_APPLY:
                self.guardar()
        elif response == gtk.RESPONSE_CANCEL:
                pass
        self.window.destroy()

    def action_changed(self, widget):
        model = self.combobox.get_model()
        action = model[self.combobox.get_active()][0]
        if action == "read":
            self.campo.set_text(_(u"Pronunciación"))
            self.entry.set_text(self.pulsador.config["pronunciacion"])
            self.campo.set_sensitive(True)
            self.entry.set_sensitive(True)
            self.ex.hide()
        elif action == "play":
            self.campo.set_text(_("Sonido"))
            self.entry.set_text(self.pulsador.config["sonido"])
            self.ex.show()
        elif action == "close" or action == "exit" or action == "fullscreen" \
            or action == "eraseall" or action == "eraselast" \
            or action == "volup" or action == "voldown":
            self.campo.set_text("")
            self.entry.set_text("")
            self.campo.set_sensitive(False)
            self.entry.set_sensitive(False)
            self.ex.hide()
        elif action == "goto":
            self.campo.set_text(_("Mosaico"))
            self.entry.set_text(self.pulsador.config["enlace_a_mosaico"])
            self.campo.set_sensitive(True)
            self.entry.set_sensitive(True)
            self.ex.show()
        elif action == "send_by_mail":
            self.campo.set_text(_("Correo"))
            self.entry.set_text(self.pulsador.config["mail"])
            self.campo.set_sensitive(True)
            self.entry.set_sensitive(True)
            self.ex.hide()
        self.actualizar(None)


    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 256, 256)
            preview.set_from_pixbuf(pixbuf)
            have_preview = True
        except:
            have_preview = False
        file_chooser.set_preview_widget_active(have_preview)

    def guardar(self):
        self.actualizar(None)
        self.pulsador_original.config = self.pulsador.config
        self.pulsador_original.aplicar_formato()
        self.pulsador_originalmosaico.config["modificado"] = False

    def actualizar(self, event, o = None):
        model = self.combobox.get_model()
        action = model[self.combobox.get_active()][0]
        fuente=(self.colorfont.get_color().red, self.colorfont.get_color().green,self.colorfont.get_color().blue)
        fondo=(self.colorback.get_color().red, self.colorback.get_color().green,self.colorback.get_color().blue)
        if action == "read":
            self.pulsador.modificar_boton(pronunciacion=self.entry.get_text())
        elif action == "play":
            self.pulsador.modificar_boton(sonido=self.entry.get_text())
        elif action == "send_by_mail":
            self.pulsador.modificar_boton(mail=self.entry.get_text())
        elif action == "goto":
            self.pulsador.modificar_boton(enlace_a_mosaico=self.entry.get_text())
        icon=self.entryimage.get_text()
        if icon and os.path.exists(icon) and not os.path.splitext(os.path.split(icon)[1])[0] in self.pulsador.actions.keys():
            pass
        elif action == "read" and not self.pulsador.config["action"] == "read":
            icon = ""
            print "no image"
        else:
            icon = "/usr/share/pixmaps/%s.png" % action
        self.pulsador.modificar_boton(action=action,
                                nombre=self.entryname.get_text(),
                                imagen=icon,
                                tipo_letra=self.fontbutton.get_font_name()[:-2],
                                tamano_letra=int(self.fontbutton.get_font_name()[-2:]),
                                escalado=int(self.hscale.get_value()),
                                color_fondo=fondo,
                                color_letra=fuente)
        
        #self.window.reshow_with_initial_size()

    def buscar_archivo(self, widget):
        model = self.combobox.get_model()
        action = model[self.combobox.get_active()][0]
        if action == "play":
            file = self.examinar("Audio")
            if file:
                self.entry.set_text(file)
                self.pulsador.modificar_boton(sonido=self.entry.get_text())
        elif action == "goto":
            file = self.examinar("Mosaico")
            if file:
                self.entry.set_text(file)
                self.pulsador.modificar_boton(enlace_a_mosaico=self.entry.get_text())

    def buscar_imagen(self, widget):
        file = self.examinar("Image")
        if file:
            self.entryimage.set_text(file)
            self.pulsador.modificar_boton(imagen=self.entryimage.get_text())

    def examinar(self, tipo):
        selected = None
        #Filtro para imagenes
        imagefilter = gtk.FileFilter()
        imagefilter.set_name(_("Imagenes"))
        imagefilter.add_mime_type("image/png")
        imagefilter.add_mime_type("image/jpeg")
        imagefilter.add_mime_type("image/gif")
        imagefilter.add_pattern("*.png")
        imagefilter.add_pattern("*.jpg")
        imagefilter.add_pattern("*.gif")
        #imagefilter.add_pattern("*.tif")
        #imagefilter.add_pattern("*.xpm")

        #Filtro para audio
        audiofilter = gtk.FileFilter()
        audiofilter.set_name(_("Audio"))
        audiofilter.add_mime_type("audio/mp3")
        audiofilter.add_mime_type("audio/ogg")
        audiofilter.add_pattern("*.mp3")
        audiofilter.add_pattern("*.ogg")

        #Filtro para mosaicos
        mosfilter = gtk.FileFilter()
        mosfilter.set_name(_("Mosaicos"))
        mosfilter.add_pattern("*.mos")

        if tipo == "Image":
            title =_("Seleccione una imagen")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(imagefilter)
            preview = gtk.Image()
            chooser.set_preview_widget(preview)
            chooser.connect("update-preview", self.update_preview_cb, preview)
            dir = config.global_config["im_dir"]
            if config.global_config["last_im_dir"]:
                dir = config.global_config["last_im_dir"]
            chooser.set_current_folder(dir)
        elif tipo == "Audio":
            title=_("Seleccione un archivo de audio")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(audiofilter)
            dir = config.global_config["aud_dir"]
            if config.global_config["last_aud_dir"]:
                dir = config.global_config["last_aud_dir"]
            chooser.set_current_folder(dir)
        elif tipo == "Mosaico":
            title=_("Seleccione una mosaico")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(mosfilter)
            chooser.set_current_folder(config.global_config["mos_dir"])

        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            selected = chooser.get_filename()
            if tipo == "Image":
                config.global_config["last_im_dir"] = os.path.dirname(selected)
                selected = self.redimensionar(selected)
            if tipo == "Audio":
                config.global_config["last_aud_dir"] = os.path.dirname(selected)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        else:
            print _(u"Opción desconocida")
        chooser.destroy()
        return selected

    def redimensionar(self, picture):
        
        size = config.global_config["resolucion_maxima"],config.global_config["resolucion_maxima"]
        quality = Image.ANTIALIAS
        path = config.temp_dir
        thumbnail = picture
        if os.path.exists(picture):
            im = Image.open(picture)
            im.thumbnail(size, quality)
            thumbnail = os.path.join(path,
            ("thumbnail_" + str(randint(1, 10**6)) + '.png'))
            while os.path.exists(thumbnail):
                thumbnail = os.path.join(path,
                ("thumbnail_" + str(randint(1, 10**6)) + '.png'))
            im.save(thumbnail, "PNG")
        del im
        return thumbnail

