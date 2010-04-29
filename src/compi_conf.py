# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import base64
import gconf_prefs
import config

# Multi-lingual support
_ = config._

class Opciones:

    def __init__(self):
        default_config = config.global_config
        # Recopilacion de las voces instaladas para festival
        available_lang = config.available_lang.keys()
        available_lang.sort()
        self.window = gtk.Dialog(_("Preferencias"), None,
         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
         (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.window.set_has_separator(True)
        self.window.set_resizable(False)
        logoad = gtk.Image()
        iconad = self.window.render_icon(gtk.STOCK_PREFERENCES, 1)
        contenedor=gtk.Notebook()
        contenedor.set_tab_pos(gtk.POS_TOP)
        contenedor.set_scrollable(False)
        fuente=gtk.Label(_("Fuente"))
        imagen=gtk.Label(_(u"Tamaño de la imagen"))
        espaciado=gtk.Label(_("Espaciado"))
        idioma=gtk.Label(_("Idioma"))
        fondo=gtk.Label(_("Color de fondo"))
        texto=gtk.Label(_("Color del texto"))
        home=gtk.Label(_("Mosaico inicial"))
        self.home_mos = gtk.Entry()
        self.home_mos.set_text(default_config["home"])
        sonidos=gtk.Label(_("Sonidos"))
        self.aud_dir = gtk.Entry()
        self.aud_dir.set_text(default_config["aud_dir"])
        imagenes=gtk.Label(_("Imagenes"))
        self.im_dir = gtk.Entry()
        self.im_dir.set_text(default_config["im_dir"])
        mosaicos=gtk.Label(_("Mosaicos"))
        self.mos_dir = gtk.Entry()
        self.mos_dir.set_text(default_config["mos_dir"])
        save=gtk.Label(_("Guardado"))
        self.save_dir = gtk.Entry()
        self.save_dir.set_text(default_config["save_dir"])
        temp=gtk.Label(_("Temporal"))
        self.temp_dir = gtk.Entry()
        self.temp_dir.set_text(config.temp_dir)
        self.lang = gtk.combo_box_new_text()
        i = 0
        active = 0
        for l in available_lang:
            self.lang.append_text(l)
            if l == default_config["idioma"]:
                active = i
            i += 1
        self.lang.set_active(active)
        
        self.user = gtk.Entry()
        self.user.set_text(default_config["usuario"])
        self.sender = gtk.Entry()
        self.sender.set_text(default_config["sender_email"])
        self.password = gtk.Entry()
        self.password.set_text(base64.b64decode(default_config["password"]))
        self.password.set_visibility(False)
        self.smtpserver = gtk.Entry()
        
        self.cabecera = gtk.Entry()
        self.cabecera.set_text(default_config["encabezado"])
        sender = gtk.Label(_("Cuenta"))
        sender.set_justify(gtk.JUSTIFY_LEFT)
        user = gtk.Label(_("Usuario"))
        user.set_justify(gtk.JUSTIFY_LEFT)
        password = gtk.Label(_(u"Contraseña"))
        header = gtk.Label(_("Asunto de los mensajes enviados:"))
        proveedores = gtk.Label(_("Proveedor:"))
        smtpserver = gtk.Label(_("Servidor SMTP"))
        self.tls = gtk.CheckButton(label=_("TLS"))
        probar = gtk.Button(label= _(u"Probar configuración"))
        probar.connect("clicked", self.test_smtp)

        refresh=gtk.Button(stock=gtk.STOCK_APPLY)
        
        exhome=gtk.Button("...")
        exhome.connect("clicked", self.buscar_mosaico, 1)
        exaud=gtk.Button("...")
        exaud.connect("clicked", self.buscar_mosaico, 5)
        exim=gtk.Button("...")
        exim.connect("clicked", self.buscar_mosaico, 6)
        exmos=gtk.Button("...")
        exmos.connect("clicked", self.buscar_mosaico, 7)
        exsave=gtk.Button("...")
        exsave.connect("clicked", self.buscar_mosaico, 8)
        self.fontbutton = gtk.FontButton("%s %d" %(default_config["tipo_letra"], default_config["size_letra"]))
        self.fontbutton.set_use_font(True)
        self.fontbutton.set_title('Fuente')
        self.colorfont = gtk.ColorButton(color=refresh.get_colormap().alloc_color(default_config["color_letra"]))
        self.colorback = gtk.ColorButton(color=refresh.get_colormap().alloc_color(default_config["color_fondo"]))
        adj = gtk.Adjustment(default_config["size_imagen"], 1.0, 8.0, 1.0, 1.0, 0.0)
        self.hscale = gtk.HScale(adj)
        self.hscale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        self.hscale.set_digits(0)
        adj2 = gtk.Adjustment(default_config["espaciado"], 1.0, 15.0, 1.0, 1.0, 0.0)
        self.espaciado = gtk.SpinButton(adj2, 1, 0)
        self.espaciado.set_wrap(True)

        #primera pestaña
        general = gtk.VBox(False, 5)
        prefered_mos = gtk.Frame(_("Rutas predeterminadas"))
        list = gtk.HBox(False, 5)
        c1 = gtk.VBox()
        c2 = gtk.VBox()
        c3 = gtk.VBox()
        
        c1.pack_start(home, False, False, 5)
        c2.pack_start(self.home_mos)
        c3.pack_start(exhome)
        c1.pack_start(sonidos, False, False, 5)
        c2.pack_start(self.aud_dir)
        c3.pack_start(exaud)
        c1.pack_start(imagenes, False, False, 5)
        c2.pack_start(self.im_dir)
        c3.pack_start(exim)
        c1.pack_start(mosaicos, False, False, 5)
        c2.pack_start(self.mos_dir)
        c3.pack_start(exmos)
        c1.pack_start(save, False, False, 5)
        c2.pack_start(self.save_dir)
        c3.pack_start(exsave)
        list.pack_start(c1)
        list.pack_start(c2, True, True, 5)
        list.pack_start(c3)
        
        save_mini = gtk.CheckButton(label=_(u"Almacenar imágenes como miniaturas"))
        use_zlib = gtk.CheckButton(label=_(u"Habilitar compresión zlib al guardar"))
        self.save_session = gtk.CheckButton(label=_(u"Guardar sesión al salir"))
        self.save_session.set_active(default_config["remember_session"])
        self.eco = gtk.CheckButton(label=_(u"Reproducir sonidos automáticamente"))
        self.eco.set_active(default_config["eco"])
        self.cleaner = gtk.CheckButton(label=_("Borrar mensaje al reproducir"))
        self.cleaner.set_active(default_config["selfcleaner"])
        self.spacer = gtk.CheckButton(label=_(u"Añadir espacio tras cada palabra"))
        self.spacer.set_active(default_config["selfspace"])
        save_mini.set_sensitive(False)
        use_zlib.set_sensitive(False)
        prefered_mos.add(list)

        general.pack_start(prefered_mos, False, False, 10)
        general.pack_start(save_mini, False, False, 5)
        general.pack_start(use_zlib, False, False, 5)
        general.pack_start(self.save_session, False, False, 5)
        general.pack_start(self.spacer, False, False, 5)
        general.pack_start(self.cleaner, False, False, 5)
        general.pack_start(self.eco, False, False, 5)
        contenedor.append_page(general, gtk.Label(_("General")))

        #segunda pestaña
        aspecto = gtk.VBox(False, 5)
        values = gtk.Frame(_("Valores por defecto"))
        v1 = gtk.HBox()
        v2 = gtk.HBox()
        v3 = gtk.HBox()
        v4 = gtk.HBox()
        v5 = gtk.HBox()
        v6 = gtk.HBox()

        v1.pack_start(fuente, False, False, 2)
        v1.pack_end(self.fontbutton, True, True, 2)
        v2.pack_start(texto, False, False, 5)
        v2.pack_start(self.colorfont, True, True, 50)
        v3.pack_start(fondo, False, False, 5)
        v3.pack_start(self.colorback,True, True, 50)

        v4.pack_start(imagen, False, False, 2)
        v4.pack_start(self.hscale, True, True, 2)
        v5.pack_start(espaciado, False, False, 2)
        v5.pack_start(self.espaciado, True, True, 50)
        v6.pack_start(idioma, False, False, 2)
        v6.pack_end(self.lang, True, True, 2)
        aspecto.pack_start(v1, False, False, 1)
        aspecto.pack_start(v6, False, False, 1)
        aspecto.pack_start(v4, False, False, 1)
        aspecto.pack_start(v2, False, False, 1)
        aspecto.pack_start(v3, False, False, 1)
        aspecto.pack_start(v5, False, False, 1)

        values.add(aspecto)
        contenedor.append_page(values, gtk.Label(_("Aspecto")))

               
        # tercera pestaña
        correo = gtk.VBox(False, 1)
        smtp_options = gtk.Frame(_("Servidor de correo saliente"))
        mail = gtk.VBox()
        m0 = gtk.HBox(False, 2)
        c2 = gtk.HBox(True, 2)
        c3 = gtk.HBox(True, 2)
        c4 = gtk.HBox()
        m1 = gtk.VBox()
        m2 = gtk.VBox()
        m1.pack_start(sender, True, True, 0)
        m2.pack_start(self.sender, True, True, 0)
        m1.pack_start(password, True, True, 0)
        m2.pack_start(self.password, True, True, 0)
        #c2.pack_start(header)
        #c2.pack_start(self.cabecera)
        c3.pack_start(proveedores)
        servers = gtk.RadioButton(group=None, label="Gmail")
        servers.connect("toggled", self.change_smtp, "smtp.gmail.com", True)
        servers.show()
        c3.pack_start(servers, True,True, 5)
        servers = gtk.RadioButton(group=servers, label="Yahoo.es")
        servers.connect("toggled", self.change_smtp, "smtp.correo.yahoo.es", False)
        servers.show()
        c3.pack_start(servers, True,True, 5)
        servers = gtk.RadioButton(group=servers, label="Otro")
        servers.connect("toggled", self.change_smtp, "", False, True)
        servers.set_active(True)
        servers.show()
        c3.pack_start(servers, True,True, 5)
        self.smtpserver.set_text(default_config["smtpserver"])
        self.tls.set_active(default_config["tls"])
        c4.pack_start(smtpserver, False, False, 10)
        c4.pack_start(self.smtpserver, True, True, 10)
        c4.pack_start(self.tls, False, False, 10)
        m0.pack_start(m1)
        m0.pack_start(m2)
        mail.pack_start(m0, True, True,2)
        mail.pack_start(c3, True, True,2)
        mail.pack_start(c4, True, True,2)

        smtp_options.add(mail)
        #correo.pack_start(c2, False, False, 3)
        correo.pack_start(smtp_options, True, True, 10)
        correo.pack_start(header, False, False, 1)
        correo.pack_start(self.cabecera, True, True, 1)
        correo.pack_start(probar, True, True, 10)
        contenedor.append_page(correo, gtk.Label(_(u"Correo electrónico")))
        
        contenedor.show_all()
        self.window.move(50,50)
        self.window.vbox.pack_start(contenedor, True, True, 10)
        response = self.window.run()
        if response == gtk.RESPONSE_ACCEPT:
                self.guardar()
        elif response == gtk.RESPONSE_CANCEL:
                pass
        self.window.destroy()

    def guardar(self):
        default_config = config.global_config
        if os.path.exists(self.home_mos.get_text()):
            default_config["home"] = self.home_mos.get_text()
        if os.path.exists(self.aud_dir.get_text()):
            default_config["aud_dir"] = self.aud_dir.get_text()
        if os.path.exists(self.im_dir.get_text()):
            default_config["im_dir"] = self.im_dir.get_text()
        if os.path.exists(self.mos_dir.get_text()):
            default_config["mos_dir"] = self.mos_dir.get_text()
        if os.path.exists(self.save_dir.get_text()):
            default_config["save_dir"] = self.save_dir.get_text()
               
        default_config["sender_email"] = self.sender.get_text()
        if self.sender.get_text().find('@') != -1:
            default_config["usuario"] = self.sender.get_text().split('@')[0]
        default_config["password"] = base64.b64encode(self.password.get_text())
        default_config["smtpserver"] = self.smtpserver.get_text()
        default_config["encabezado"] = self.cabecera.get_text()
        default_config["tls"] = self.tls.get_active()
        default_config["remember_session"] = self.save_session.get_active()
        default_config["selfcleaner"] = self.cleaner.get_active()
        default_config["selfspace"] = self.spacer.get_active()
        default_config["eco"] = self.eco.get_active()
        
        model = self.lang.get_model()
        active = self.lang.get_active()
        default_config["idioma"] = model[active][0]


        #default_config["user"] = self.user.get_text()
        cfont = (self.colorfont.get_color().red, self.colorfont.get_color().green,self.colorfont.get_color().blue)
        cbackg = (self.colorback.get_color().red, self.colorback.get_color().green,self.colorback.get_color().blue)
        default_config["color_letra"] = tohex(cfont)
        default_config["color_fondo"] = tohex(cbackg)
        default_config["tipo_letra"] = self.fontbutton.get_font_name()[:-2]
        default_config["size_letra"] = int(self.fontbutton.get_font_name()[-2:])
        default_config["size_imagen"] = int(self.hscale.get_value())
        default_config["espaciado"] = self.espaciado.get_value_as_int()
        prefs = gconf_prefs.AutoPrefs('/apps/compi/', default_config)
        config.global_config = default_config
        prefs.gconf_save()
        
        voice = config.get_voice()
        if voice:
            config.player.set_voice(voice)

    def buscar_mosaico(self, widget, n):
        if n <= 4:
            file = self.examinar("Mosaico")
        else:
            file = self.examinar()
        if file:
            if n == 5:
                self.aud_dir.set_text(file)
            elif n == 6:
                self.im_dir.set_text(file)
            elif n == 7:
                self.mos_dir.set_text(file)
            elif n == 8:
                self.save_dir.set_text(file)
            elif n == 1:
                self.home_mos.set_text(file)

    def change_smtp(self, widget, smtpserver, tls, sensitive = False):
        self.smtpserver.set_sensitive(sensitive)
        self.tls.set_sensitive(sensitive)
        self.smtpserver.set_text(smtpserver)
        self.tls.set_active(tls)

    def test_smtp(self, widget):
        import smtplib
        from email.MIMEText import MIMEText
        from email.Header import Header
       
        smtpserver= self.smtpserver.get_text()
        sender = self.sender.get_text()
        user= self.sender.get_text().split('@')[0]
        password = self.password.get_text()
        tls= self.tls.get_active()
        
        try:
            server = smtplib.SMTP(smtpserver)
            server.set_debuglevel(1)
            server.ehlo(sender)
            if tls:
                server.starttls()
                server.ehlo(sender)
            try:
                server.login(user, password)
            except:
                res = _(u"Fallo de autenticación")
            else:
                res =  _(u"Configuración correcta")
            server.quit()
        except:
            res = _("Fallo al conectar al servidor SMTP: ") + smtpserver
        aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_OK, gtk.RESPONSE_CLOSE))
        mensaje = gtk.Label(res)
        logoad = gtk.Image()
        iconad = aviso.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
        aviso.set_icon(iconad)
        aviso.vbox.pack_start(mensaje)
        aviso.show_all()
        aviso.run()
        aviso.destroy()

    def examinar(self, tipo = None):
        selected = None

        #Filtro para mosaicos
        mosfilter = gtk.FileFilter()
        mosfilter.set_name(_("Mosaicos"))
        mosfilter.add_pattern("*.mos")

        if not tipo:
            title =_("Seleccione una carpeta")
            chooser = gtk.FileChooserDialog(title, None, action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        elif tipo == "Mosaico":
            title=_("Seleccione un mosaico")
            chooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.add_filter(mosfilter)
        chooser.set_current_folder(os.path.expanduser('~'))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            selected = chooser.get_filename()
            if tipo == "Image":
                selected = self.redimensionar(selected)
        elif response == gtk.RESPONSE_CANCEL:
            pass
        else:
            print _(u"Opción desconocida")
        chooser.destroy()
        return selected
        
def tohex(rgb):
    zero = "0000"
    red = (zero+hex(rgb[0]/256)[2:])[-2:]
    green = (zero+hex(rgb[1]/256)[2:])[-2:]
    blue = (zero+hex(rgb[2]/256)[2:])[-2:]
    return "#%s%s%s" % (red, green, blue)

