# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
gtk.gdk.threads_init()
from threading import Timer
from config import _

class aviso_temp:
    
    def __init__(self, msg, timeout = None):
        """
        Clase auxiliar para mostrar mensajes de aviso
        """
        self.aviso = gtk.Dialog(_('Aviso'), None, gtk.DIALOG_DESTROY_WITH_PARENT,
             (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
        self.timeout = timeout
        self.tick = 0.1
        self.fraction = self.tick/self.timeout
        mensaje = gtk.Label(msg)
        mensaje.set_line_wrap(True)
        mensaje.set_max_width_chars(80)
        logoad = gtk.Image()
        iconad = self.aviso.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
        self.countdown = gtk.ProgressBar()
        self.countdown.set_fraction(1.0)
        self.aviso.set_icon(iconad)
        self.aviso.vbox.pack_start(mensaje, True, True, 10)
        self.aviso.vbox.pack_start(self.countdown, True, True, 5)
        self.aviso.show_all()
        if self.timeout:
            self.t = Timer(self.tick, self.update)
            self.t.start()
        self.response = self.aviso.run()
        self.t.cancel()
        self.aviso.destroy()

    def update(self):
        self.timeout -= self.tick
        if self.timeout > 0:
            gtk.gdk.threads_enter()
            self.countdown.set_fraction(self.countdown.get_fraction() - self.fraction)
            gtk.gdk.threads_leave()
            self.t = Timer(self.tick, self.update)
            self.t.start()
        else:
            gtk.gdk.threads_enter()
            self.aviso.response( gtk.RESPONSE_ACCEPT)
            gtk.gdk.threads_leave()
