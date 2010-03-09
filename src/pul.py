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

_ = config._

copy = None

class Pulsador (gtk.Button):

    def __init__(self, tipo = None, path=None):
        gtk.Button.__init__(self)
        box = gtk.VBox(False, 0)
        box.set_border_width(2)
        self.ident = randint(1, 10**8)
        self.tipo = tipo
        if tipo == "contacto":
            self.default_image = "/usr/share/pixmaps/login-photo.png"
        else:
            self.default_image = ""
        self.player = config.player
        self.ispreview = False
        self.ismini = False
        self.ismodificable = True
        self.path = path
        self.default_config={
        "nombre":"Haga clic con el\n botón derecho\n para editar", \
        "tipo_letra":config.global_config["tipo_letra"], \
        "color_letra":config.global_config["color_letra"], \
        "size_letra":config.global_config["size_letra"], \
        "color_fondo":config.global_config["color_fondo"], \
        "escalado_imagen":config.global_config["size_imagen"], \
        "pronunciacion":"", \
        "sonido":"", \
        "imagen":self.default_image, \
        "enlace_a_mosaico":"", \
        }
        self.config = self.default_config
        self.imagen = gtk.Image()
        self.titulo = gtk.Label("")
        box.pack_start(self.imagen, True, True, 0)
        box.pack_start(self.titulo, False, False, 0)
        self.add(box)
        self.connect_object("event", self.button_press, self)
        self.aplicar_formato()
        self.show_all()


    #Metodos
    def aplicar_formato(self):
        self.titulo.set_use_markup(True)
        if self.config["color_fondo"]:
            self.modify_bg(gtk.STATE_NORMAL,
            self.get_colormap().alloc_color(self.config["color_fondo"]))
        self.titulo.set_markup("<span font_desc=\"%s %d \" foreground=\"%s\">%s</span>" % (self.config["tipo_letra"], self.config["size_letra"], self.config["color_letra"], self.config["nombre"]))
        if self.config["imagen"] and os.path.exists(self.config["imagen"]):
            x = self.ismini and 1 or self.config["escalado_imagen"]
            size = x*32, x*32
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.config["imagen"], size[0], size[1])
            self.imagen.set_from_pixbuf(pixbuf)
        self.show_all()

    def modificar_boton(self, nombre=None, pronunciacion=None, sonido=None, tipo_letra=None, color_letra=None, tamano_letra=None, color_fondo=None, imagen="",  enlace_a_mosaico=None, escalado=0):
        if self.ismodificable:
            self.config["nombre"] = nombre and nombre or self.config["nombre"]
            self.config["tipo_letra"] = tipo_letra and tipo_letra or self.config["tipo_letra"]
            self.config["color_letra"] = color_letra and self.tohex(color_letra)  or self.config["color_letra"]
            self.config["size_letra"] = tamano_letra and tamano_letra or self.config["size_letra"]
            self.config["color_fondo"] =  color_fondo and self.tohex(color_fondo) or self.config["color_fondo"]
            self.config["pronunciacion"] = pronunciacion and pronunciacion or self.config["pronunciacion"]
            self.config["sonido"] = sonido and sonido or self.config["sonido"]
            self.config["imagen"] = imagen #and imagen or self.config["imagen"]
            self.config["escalado_imagen"] = escalado and escalado or self.config["escalado_imagen"]
            self.config["enlace_a_mosaico"] = enlace_a_mosaico and enlace_a_mosaico or self.config["enlace_a_mosaico"]
            self.aplicar_formato()

    def limpiar_boton(self):
        self.config = self.default_config
        self.aplicar_formato()

    def from_string(self, ident, s):
        path = config.temp_dir
        self.ident = ident
        for k, v in s.iteritems():
            if k == "imagen" and v:
                try:
                    file = str(os.path.join(path, v["file"]))
                    f = open(file,"w")
                    f.write(base64.b64decode(v["data"]))
                    f.close()
                    self.config["imagen"] = file
                except:
                    print "Fallo al recuperar la imagen"
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
                    p += tab + "\t<%s>\n" % k
                    p += tab + "\t\t<file>%s</file>\n" % f
                    p += tab + "\t\t<coding>%s</coding>\n" % "base64"
                    p += tab + "\t\t<zlib-compressed>%s</zlib-compressed>\n" % compress
                    p += tab + "\t\t<data>%s</data>\n" % b64
                    p += tab + "\t</%s>\n" % k

                    audio.close()
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
                    p += tab + "\t<%s>\n" % k
                    p += tab + "\t\t<file>%s</file>\n" % f
                    p += tab + "\t\t<coding>%s</coding>\n" % "base64"
                    p += tab + "\t\t<zlib-compressed>%s</zlib-compressed>\n" % compress
                    p += tab + "\t\t<data>%s</data>\n" % b64
                    p += tab + "\t</%s>\n" % k
                    picture.close()
                except:
                    pass
            else:
                r += tab + "\t<%s>%s</%s>\n" % (k, v , k)
        r += p + tab + "</Pulsador_%s>\n" % (self.ident)
        return r

    def button_press(self, widget, event):
        # global base
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button==1:
                #print "Click con el botón izquierdo"
                if self.tipo == "contacto":
                        self.enviar_correo()
                else:
                    gobject.idle_add(widget.leer)
                    # insertar en la salida
                    if not (widget.ispreview or widget.ismini):
                        self.insertar()
            elif event.button==2:
                #print "Click con el botón central"
                # copiar boton
                if widget.ismodificable and not widget.ispreview and not config.gui.fullscreen:
                    global copy
                    if copy:
                        #print "Intercambiar con Pulsador en memoria"
                        if copy.tipo == widget.tipo:
                            t = widget.config
                            widget.config = copy.config
                            copy.config = t
                            widget.aplicar_formato()
                        copy.set_relief(gtk.RELIEF_NORMAL)
                        copy.aplicar_formato()
                        copy = None
                    else:
                        #print "Almacenar Pulsador en memoria"
                        copy = widget
                        copy.set_relief(gtk.RELIEF_NONE)
            elif event.button==3:
                #print "Click con el botón derecho"
                if widget.ismodificable and not widget.ispreview and not config.gui.fullscreen:
                    #print "Editar Pulsador"
                    # mostrar ventana edición
                    p = Propiedades(widget)

    def clone(self):
        b = Pulsador()
        b.config = self.config
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

    def leer(self):
        if not config.gui.muted:
            if self.config["sonido"]:
                print "Reproduciendo archivo de audio del Pulsador [%s]...\t" % self.config["nombre"]
                self.player.play_audio(self.config["sonido"])
            elif self.config["pronunciacion"]:
                print "Leyendo el Pulsador [%s]...\t" % self.config["nombre"]
                self.player.read_text(self.config["pronunciacion"])
                
    def insertar(self):
        out = config.gui.out
        w, h = out["layout"].get_size()
        relative = os.path.join(self.path, os.path.split(self.config["enlace_a_mosaico"])[1])
        print relative
        if self.config["enlace_a_mosaico"]:
            if os.path.exists(self.config["enlace_a_mosaico"]):
                print "Abriendo mosaico %s..." % os.path.split(self.config["enlace_a_mosaico"])[1]
                config.gui.abrir(None, self.config["enlace_a_mosaico"])
            elif os.path.exists(relative):
                print "Abriendo mosaico %s..." % os.path.split(relative)[1]
                config.gui.abrir(None, relative)
            else:
                aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
                 (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
                mensaje = gtk.Label(_("No se puede acceder al archivo %s. Revise que existe y que tiene permisos de lectura." % self.config["enlace_a_mosaico"]))
                aviso.vbox.pack_start(mensaje)
                aviso.show_all()
                aviso.run()
                aviso.destroy()

        elif self.config["sonido"]:
            out["texto"].insert(out["texto"].get_end_iter(), " #" + self.config["nombre"] + "# ")
            m = self.mini()
            out["imagenes"].append(m)
            out["layout"].put(m, ((len(out["imagenes"]) - 1) * 100) % w , (((len(out["imagenes"]) - 1) * 100) / w)*100)

        elif self.config["pronunciacion"]:
            out["texto"].insert(out["texto"].get_end_iter(), self.config["nombre"])
            m = self.mini()
            out["imagenes"].append(m)
            out["layout"].put(m, ((len(out["imagenes"]) - 1) * 100) % w, (((len(out["imagenes"]) - 1) * 100) / w)*100)
    
    def enviar_correo(self, coding = 'utf-8'):
        sender = config.global_config["sender_email"]
        user = config.global_config["usuario"]
        header = config.global_config["encabezado"]
        receiver = self.config["enlace_a_mosaico"]
        text = config.gui.out["texto"].get_text(config.gui.out["texto"].get_start_iter(),
                config.gui.out["texto"].get_end_iter())
        password = base64.b64decode(config.global_config["password"])
        smtpserver = config.global_config["smtpserver"]
        tls = config.global_config["tls"]
        if sender and password and smtpserver:
            aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
             (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
            mensaje = gtk.Label(_("El siguiente mensaje se enviará automáticamente en 5 segundos"))
            
            de = gtk.Label(_("DE:")+sender)
            de.set_alignment(0, 0)
            para = gtk.Label(_("PARA:")+receiver)
            para.set_alignment(0, 0)
            asunto = gtk.Label(_("ASUNTO:")+header)
            asunto.set_alignment(0, 0)
            contenido = gtk.Label(text)
            contenido.set_alignment(0, 0)
            
            logoad = gtk.Image()
            iconad = aviso.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
            aviso.set_icon(iconad)
            
            aviso.vbox.pack_start(mensaje)
            aviso.vbox.pack_start(gtk.HSeparator())
            aviso.vbox.pack_start(de)
            aviso.vbox.pack_start(para)
            aviso.vbox.pack_start(asunto)
            aviso.vbox.pack_start(contenido)
            aviso.show_all()
            
            timer = gobject.timeout_add(5000, aviso.destroy)
            response = aviso.run()
            if response == gtk.RESPONSE_CLOSE:
                gobject.source_remove(timer)
                aviso.destroy()
                return 0
            else:
                aviso.destroy()
                import smtplib
                from email.MIMEText import MIMEText
                from email.Header import Header
                
                body = unicode(text, 'utf-8')
                msg = MIMEText(body.encode(coding), 'plain', coding)
                msg['From']    = sender
                msg['To']      = receiver
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
                        print "Fallo de autenticación"
                        return 0
                    else:
                        server.sendmail(sender, receiver, msg.as_string())
                    server.quit()
                    return 1
        else:
            aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
             (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
            mensaje = gtk.Label(_("No ha configurado aún las opciones de correo saliente."))
            aviso.vbox.pack_start(mensaje)
            aviso.run()
            aviso.show_all()
            aviso.destroy()


class Propiedades:

    def __init__(self, p):
        self.pulsador_original = p
        self.pulsador = p.preview()
        self.window = gtk.Dialog(_("Propiedades del Pulsador"), None,
         gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.window.set_has_separator(True)
        
        contenedor=gtk.Table(6, 4, False)
        contenedor.set_row_spacing(4, 5)
        contenedor.set_row_spacing(5, 20)

        name=gtk.Label(_("Nombre"))
        pron=gtk.Label(_("Pronunciación"))
        sound=gtk.Label(_("Sonido"))
        image=gtk.Label(_("Imagen"))
        mos=gtk.Label(_("Mosaico"))
        dir=gtk.Label(_("Dirección de correo"))
        fondo=gtk.Label(_("Color de fondo"))
        texto=gtk.Label(_("Color del texto"))
        
        self.entryname = gtk.Entry()
        self.entryname.set_text(p.config["nombre"])
        self.entrypron = gtk.Entry()
        self.entrypron.set_text(p.config["pronunciacion"])
        self.entrysound = gtk.Entry()
        self.entrysound.set_text(p.config["sonido"])
        self.entryimage = gtk.Entry()
        self.entryimage.set_text(p.config["imagen"])
        self.entrymos= gtk.Entry()
        self.entrymos.set_text(p.config["enlace_a_mosaico"])
        
        ex1=gtk.Button(_("Examinar"))
        ex1.connect("clicked", self.buscar_sonido)
        ex2=gtk.Button(_("Examinar"))
        ex2.connect("clicked", self.buscar_imagen)
        ex3=gtk.Button(_("Examinar"))
        ex3.connect("clicked", self.buscar_mosaico)
        
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
        self.entrypron.connect("focus-out-event", self.actualizar)
        
        
        if not player.pymedia_installed or p.tipo=="contacto":
            sound.set_sensitive(False)
            self.entrysound.set_sensitive(False)
            ex1.set_sensitive(False)
            
        #primera columna
        contenedor.attach(self.pulsador, 0, 1, 0, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK, 10, 10)

        contenedor.attach(texto, 0, 1, 5, 6, gtk.SHRINK, gtk.SHRINK, 0, 0)

        #seguna columna
        contenedor.attach(name, 1, 2, 0, 1, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(pron, 1, 2, 1, 2, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(sound, 1, 2, 2, 3, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(image, 1, 2, 3, 4, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        if p.tipo == "contacto":
            contenedor.attach(dir, 1, 2, 4, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        else:
            contenedor.attach(mos, 1, 2, 4, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.colorfont, 1, 2, 5, 6, gtk.SHRINK, gtk.SHRINK, 0, 0)


        #tercera columna
        contenedor.attach(self.entryname, 2, 3, 0, 1, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.entrypron, 2, 4, 1, 2, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.entrysound, 2, 3, 2, 3, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        #contenedor.attach(self.entryimage, 2, 3, 3, 4, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.hscale, 2, 3, 3, 4, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        if p.tipo == "contacto":
            contenedor.attach(self.entrymos, 2, 4, 4, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        else:
            contenedor.attach(self.entrymos, 2, 3, 4, 5, gtk.SHRINK|gtk.FILL, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(fondo, 2, 3, 5, 6, gtk.SHRINK, gtk.SHRINK, 0, 0)


        #cuarta columna
        contenedor.attach(self.fontbutton, 3, 4, 0, 1, gtk.SHRINK, gtk.SHRINK, 0, 0)
        contenedor.attach(ex1, 3, 4, 2, 3, gtk.SHRINK, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(ex2, 3, 4, 3, 4, gtk.SHRINK, gtk.SHRINK|gtk.FILL, 0, 0)
        if not p.tipo == "contacto":
            contenedor.attach(ex3, 3, 4, 4, 5, gtk.SHRINK, gtk.SHRINK|gtk.FILL, 0, 0)
        contenedor.attach(self.colorback, 3, 4, 5, 6, gtk.SHRINK, gtk.SHRINK, 0, 0)

        self.window.vbox.pack_start(contenedor)
        contenedor.show_all()
        self.window.move(150,150)
        response = self.window.run()

        if response == gtk.RESPONSE_ACCEPT:
                self.guardar()
        elif response == gtk.RESPONSE_APPLY:
                self.guardar()
        elif response == gtk.RESPONSE_CANCEL:
                pass
        self.window.destroy()

    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
            preview.set_from_pixbuf(pixbuf)
            have_preview = True
        except:
            have_preview = False
        file_chooser.set_preview_widget_active(have_preview)

    def guardar(self):
        self.actualizar(None)
        self.pulsador_original.config = self.pulsador.config
        self.pulsador_original.aplicar_formato()

    def actualizar(self, event, o = None):
        fuente=(self.colorfont.get_color().red, self.colorfont.get_color().green,self.colorfont.get_color().blue)
        fondo=(self.colorback.get_color().red, self.colorback.get_color().green,self.colorback.get_color().blue)
        self.pulsador.modificar_boton(nombre=self.entryname.get_text(),
                                pronunciacion=self.entrypron.get_text(),
                                imagen=self.entryimage.get_text(),
                                sonido=self.entrysound.get_text(),
                                enlace_a_mosaico=self.entrymos.get_text(),
                                tipo_letra=self.fontbutton.get_font_name()[:-2],
                                tamano_letra=int(self.fontbutton.get_font_name()[-2:]),
                                escalado=int(self.hscale.get_value()),
                                color_fondo=fondo,
                                color_letra=fuente)
        #self.window.reshow_with_initial_size()

    def buscar_sonido(self, widget):
        file = self.examinar("Audio")
        if file:
            self.entrysound.set_text(file)
            self.pulsador.modificar_boton(sonido=self.entrysound.get_text())

    def buscar_imagen(self, widget):
        file = self.examinar("Image")
        if file:
            self.entryimage.set_text(file)
            self.pulsador.modificar_boton(imagen=self.entryimage.get_text())

    def buscar_mosaico(self, widget):
        file = self.examinar("Mosaico")
        if file:
            self.entrymos.set_text(file)
            self.pulsador.modificar_boton(enlace_a_mosaico=self.entrymos.get_text())

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
            chooser.set_current_folder(config.global_config["im_dir"])
        elif tipo == "Audio":
            title=_("Seleccione una archivo de audio")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(audiofilter)
            chooser.set_current_folder(config.global_config["aud_dir"])
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
                selected = self.redimensionar(selected)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        else:
            print _("Opción desconocida")
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

