# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import time
import base64
import os
import config

from xml.dom.minidom import parse
from zlib import compress
from calendar import timegm
from pul import Pulsador

# Multi-lingual support
_ = config._


# Recopilacion de las voces instaladas para festival
available_lang = config.available_lang

class Mosaico(gtk.Frame):
    """
    Clase que representa los paneles de pulsadores
    """
    
    def __init__(self, nombre, filas, columnas, ruta = "", padre=None):
        """
        Constructor de la clase
        """
        gtk.Frame.__init__(self)
        self.rejilla = gtk.Table(filas, columnas, True)
        self.default_config = config.global_config
        self.padre = padre
        self.config={"filas":filas, \
            "columnas":columnas, \
            "nombre":nombre, \
            "fecha_creacion":time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()), \
            "tabla_botones":[], \
            "modificable":True, \
            "solo_lectura":False, \
            "espaciado":self.default_config["espaciado"], \
            "modificado":False, \
            "ruta_guardado":ruta, \
            "idioma":self.default_config["idioma"]
            }
        if os.path.exists(ruta):
            self.cargar_mosaico()
        else:
            for i in range(filas):
                self.config["tabla_botones"].append([])
                for j in range(columnas):
                    if nombre == "*Contactos*":
                        p = Pulsador( tipo = "contacto")
                    else:
                        p = Pulsador()
                    self.config["tabla_botones"][i].append(p)
            self.dibujar_tabla()
        self.add(self.rejilla)

    #Metodos
    def dibujar_tabla(self):
        """
        Coloca los pulsadores en su lugar correspondiente
        """
        f, c = self.config["filas"], self.config["columnas"]
        self.rejilla.resize(f, c)
        for i in range(f):
            self.rejilla.set_row_spacing(i, self.config["espaciado"])
            for j in range(c):
                p = self.config["tabla_botones"][i][j]
                self.rejilla.attach(p, j, j+1, i, i+1,
                gtk.SHRINK | gtk.EXPAND | gtk.FILL,
                gtk.SHRINK | gtk.EXPAND | gtk.FILL, 0, 0)
                self.rejilla.set_col_spacing(j, self.config["espaciado"])
        self.show_all()

    def ajustar_espacio(self):
        """
        Configura la separacion entre filas y columnas
        """
        f, c = self.config["filas"], self.config["columnas"]
        for i in range(f):
            self.rejilla.set_row_spacing(i, self.config["espaciado"])
            for j in range(c):
                self.rejilla.set_col_spacing(j, self.config["espaciado"])

    

    def get_nombre(self):
        """
        Devuelve el nombre del mosaico
        """
        return self.config["nombre"]

    def insertar_columna(self):
        """
        Añade una columna de pulsadores editables
        """
        j = self.config["columnas"]
        self.config["columnas"] += 1
        f, c = self.config["filas"], self.config["columnas"]
        self.rejilla.resize(f, c)
        for i in range (self.config["filas"]):
            p= Pulsador(None, self)
            self.config["tabla_botones"][i].append(p)
            self.rejilla.set_row_spacing(i, self.config["espaciado"])
            self.rejilla.attach(p, j, j+1, i, i+1,
            gtk.SHRINK|gtk.EXPAND|gtk.FILL,
            gtk.SHRINK|gtk.EXPAND|gtk.FILL, 0, 0)
        self.rejilla.set_col_spacing(j, self.config["espaciado"])
        self.config["modificado"] = True
        self.show_all()

    def insertar_fila(self):
        """
        Añade una fila de pulsadores editables
        """
        i = self.config["filas"]
        self.config["filas"] += 1
        self.config["tabla_botones"].append([])
        f, c = self.config["filas"], self.config["columnas"]
        self.rejilla.resize(f, c)
        for j in range (self.config["columnas"]):
            p= Pulsador(None, self)
            self.config["tabla_botones"][i].append(p)
            self.rejilla.attach(p, j, j+1, i, i+1,
            gtk.SHRINK|gtk.EXPAND|gtk.FILL,
            gtk.SHRINK|gtk.EXPAND|gtk.FILL, 0, 0)
            self.rejilla.set_col_spacing(j, self.config["espaciado"])
        self.rejilla.set_row_spacing(i, self.config["espaciado"])
        self.config["modificado"] = True
        self.show_all()

    def borrar_columna(self):
        """
        Borra la última columna
        """
        if self.config["columnas"] > 1:
            for i in range (self.config["filas"]):
                self.config["tabla_botones"][i].pop()
            self.config["columnas"] -= 1
            f, c = self.config["filas"], self.config["columnas"]
            self.remove(self.rejilla)
            self.rejilla = gtk.Table(f, c, True)
            self.add(self.rejilla)
            for i in range(f):
                self.rejilla.set_row_spacing(i, self.config["espaciado"])
                for j in range(c):
                    p = self.config["tabla_botones"][i][j].clone()
                    self.rejilla.attach(p, j, j+1, i, i+1,
                    gtk.SHRINK|gtk.EXPAND|gtk.FILL,
                    gtk.SHRINK|gtk.EXPAND|gtk.FILL, 0, 0)
                    self.rejilla.set_col_spacing(j, self.config["espaciado"])
            self.config["modificado"] = True
            self.show_all()

    def cambiar_idioma(self):
        try:
            config.player.set_voice(config.available_lang[self.config["idioma"]])
        except:
            print "Error al cambiar el idioma"

    def borrar_fila(self):
        """
        Borra la última fila
        """
        if self.config["filas"] > 1:
            self.config["filas"] -= 1
            self.config["tabla_botones"][self.config["filas"]].pop()
            f, c = self.config["filas"], self.config["columnas"]
            self.remove(self.rejilla)
            self.rejilla = gtk.Table(f, c, True)
            self.add(self.rejilla)
            for i in range(f):
                self.rejilla.set_row_spacing(i, self.config["espaciado"])
                for j in range(c):
                    p = self.config["tabla_botones"][i][j].clone()
                    self.rejilla.attach(p, j, j+1, i, i+1,
                    gtk.SHRINK|gtk.EXPAND|gtk.FILL,
                    gtk.SHRINK|gtk.EXPAND|gtk.FILL, 0, 0)
                    self.rejilla.set_col_spacing(j, self.config["espaciado"])
            self.config["modificado"] = True
            self.show_all()

    def cargar_mosaico(self, ruta = None):
        """
        Recupera la información del archivo guardado previamente
        """
        if ruta:
            self.config["ruta_guardado"] = ruta
        try:
            dom = parse(self.config["ruta_guardado"])
            dic = nodeToDic(dom)["mosaico"]
        except:
            print "Error al parsear el archivo %s" % self.config["ruta_guardado"]
        else:
            if dic["nombre"] == "*Contactos*":
                tipo = "contacto"
            else:
                tipo = None
            for i in range(int(dic["filas"])):
                self.config["tabla_botones"].append([])
                for j in range(int(dic["columnas"])):
                    self.config["tabla_botones"][i].append(None)
            for k, v in dic.iteritems():
                if k == "tabla_botones":
                    for ident, config in v.iteritems():
                        p = Pulsador(tipo, self)
                        i, j = p.from_string(ident.replace("Pulsador_", ""), config)
                        self.config["tabla_botones"][i][j] = p
                elif k == "ruta_guardado":
                    pass
                elif k == "espaciado" or k == "filas" or k == "columnas":
                    self.config[str(k)] = int(v)
                elif k == "fecha_creacion":
                    try:
                        self.config[str(k)] = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(timegm(eval(str(v)))))
                    except:
                        self.config[str(k)] = str(v)
                else:
                    if v == "True":
                        v = True
                    elif v == "False":
                        v = False
                    self.config[str(k)] = v
            self.dibujar_tabla()

    def guardar_mosaico(self, ruta = None):
        """
        Almacena la información del objeto en un archivo
        """
        try:
            self.config["modificado"] = False
            save = self.to_string()
            if ruta:
                self.config["ruta_guardado"] = ruta
            s = open(self.config["ruta_guardado"],'w')
            #if default_config["use_zlib"]:
            #    save = zlib.compress(save, default_config["level_zlib"])
            s.write(save)
            s.close()
            #print save
        except:
            self.config["modificado"] = True
            print "Fallo al guardar el mosaico"

    def to_string(self):
        """
        Genera una cadena en xml con la información del objeto
        """
        s = "<?xml version=\"1.0\" ?>\n"
        p = ""
        s += "<mosaico>\n"
        for k, v in self.config.iteritems():
            if k == "tabla_botones" and v:
                p += "\t<%s>\n" % (k)
                f, c = self.config["filas"], self.config["columnas"]
                for i in range(f):
                    for j in range(c):
                        p += self.config["tabla_botones"][i][j].to_string(i, j)
                p += "\t</%s>\n" % k
            else:
                s += "\t<%s>%s</%s>\n" % (k,v,k)

        s +=  p + "</mosaico>\n\n"

        return s
        
    def formato(self, parent = None):
        """
        Muestra la ventana de configuración de aspecto
        """
        window = gtk.Dialog(_("Formato"), parent,
         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        window.set_has_separator(True)
        
        logoad = gtk.Image()
        iconad = window.render_icon(gtk.STOCK_PREFERENCES, 1)
        nombreL=gtk.Label(_("Nombre"))
        fuente=gtk.CheckButton(_("Fuente"))
        imagen=gtk.CheckButton(_("Tamaño de la imagen"))
        espaciadoL=gtk.Label(_("Espaciado"))
        idioma=gtk.Label(_("Idioma"))
        fondo=gtk.CheckButton(_("Color de fondo"))
        texto=gtk.CheckButton(_("Color del texto"))
        update_all = gtk.Label("")
        update_all.set_markup("<i>"+_("Seleccione los campos que desee actualizar")+"</i>")
        update_all.set_justify(gtk.JUSTIFY_CENTER)
        lang = gtk.combo_box_new_text()
        i = 0
        active = 0
        default = 0
        for l in available_lang:
            lang.append_text(l)
            if l == self.config["idioma"]:
                active = i
            if l == config.global_config["idioma"]:
                default = i
            i += 1
        if active:
            lang.set_active(active)
        else:
            lang.set_active(default)
        nombre = gtk.Entry()
        nombre.set_text(self.config["nombre"])
        fontbutton = gtk.FontButton("%s %d" %(config.global_config["tipo_letra"], config.global_config["size_letra"]))
        fontbutton.set_use_font(True)
        fontbutton.set_title('Fuente')
        colorfont = gtk.ColorButton(color=fontbutton.get_colormap().alloc_color(config.global_config["color_letra"]))
        colorback = gtk.ColorButton(color=fontbutton.get_colormap().alloc_color(config.global_config["color_fondo"]))
        adj = gtk.Adjustment(config.global_config["size_imagen"], 1.0, 10.0, 1.0, 1.0, 0.0)
        hscale = gtk.HScale(adj)
        hscale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        hscale.set_digits(0)
        adj2 = gtk.Adjustment(self.config["espaciado"], 1.0, 15.0, 1.0, 1.0, 0.0)
        espaciado = gtk.SpinButton(adj2, 1, 0)
        espaciado.set_wrap(True)

        aspecto1 = gtk.VBox(False, 5)
        aspecto2 = gtk.VBox(False, 5)
        mosaic = gtk.Frame(_("Formato del mosaico"))
        puls = gtk.Frame(_("Formato de los pulsadores"))

        v0 = gtk.HBox()
        v1 = gtk.HBox()
        v2 = gtk.HBox()
        v3 = gtk.HBox()
        v4 = gtk.HBox()
        v5 = gtk.HBox()
        v6 = gtk.HBox()

        v0.pack_start(nombreL, False, False, 2)
        v0.pack_end(nombre, True, True, 2)
        v3.pack_start(fuente, False, False, 2)
        v3.pack_end(fontbutton, True, True, 2)
        v5.pack_start(texto, False, False, 2)
        v5.pack_start(colorfont, False, False, 2)
        v5.pack_end(colorback, False, False, 2)
        v5.pack_end(fondo, False, False, 2)
        v4.pack_start(imagen, False, False, 2)
        v4.pack_start(hscale, True, True, 2)
        v2.pack_start(espaciadoL, False, False, 2)
        v2.pack_start(espaciado, False, False, 2)
        v1.pack_start(idioma, False, False, 2)
        v1.pack_end(lang, True, True, 2)
        v6.pack_start(update_all, True, True, 2)

        aspecto1.pack_start(v0, False, False, 1)
        aspecto1.pack_start(v1, False, False, 1)
        aspecto1.pack_start(v2, False, False, 1)
        aspecto2.pack_start(v3, False, False, 1)
        aspecto2.pack_start(v4, False, False, 1)
        aspecto2.pack_start(v5, False, False, 1)
        aspecto2.pack_start(v6, False, False, 1)
        #aspecto.pack_start(v0, False, False, 1)

        mosaic.add(aspecto1)
        mosaic.show_all()

        puls.add(aspecto2)
        puls.show_all()

        window.move(150,150)
        window.vbox.pack_start(mosaic, True, True, 10)
        window.vbox.pack_start(puls, True, True, 10)

        response = window.run()
        if response == gtk.RESPONSE_ACCEPT:
            cfont = (colorfont.get_color().red, colorfont.get_color().green, colorfont.get_color().blue)
            cbackg = (colorback.get_color().red, colorback.get_color().green,colorback.get_color().blue)
            self.config["nombre"] = nombre.get_text()
            self.config["espaciado"] = espaciado.get_value_as_int()
            model = lang.get_model()
            active = lang.get_active()
            self.config["idioma"] = model[active][0]

            self.ajustar_espacio()
            for fila in self.config["tabla_botones"]:
                for p in fila:
                    if fuente.get_active():
                        p.modificar_boton(imagen = p.config["imagen"], tipo_letra = fontbutton.get_font_name()[:-2], tamano_letra=int(fontbutton.get_font_name()[-2:]))
                    if imagen.get_active():
                        p.modificar_boton(imagen = p.config["imagen"], escalado=int(hscale.get_value()))
                    if texto.get_active():
                        p.modificar_boton(imagen = p.config["imagen"], color_letra=cfont)
                    if fondo.get_active():
                        p.modificar_boton(imagen = p.config["imagen"], color_fondo=cbackg)
                    p.show_all()
            self.show_all()
        elif response == gtk.RESPONSE_CANCEL:
                pass
        window.destroy()
        

class NotTextNodeError:
    pass


def getTextFromNode(node):
    """
    scans through all children of node and gathers the
    text. if node has non-text child-nodes, then
    NotTextNodeError is raised.
    """
    t = ""
    for n in node.childNodes:
        if n.nodeType == n.TEXT_NODE:
            t += n.nodeValue
        else:
            raise NotTextNodeError
    return t


def nodeToDic(node):
    """
    nodeToDic() scans through the children of node and makes a
    dictionary from the content.
    three cases are differentiated:
        - if the node contains no other nodes, it is a text-node
    and {nodeName:text} is merged into the dictionary.
        - if the node has the attribute "method" set to "true",
    then it's children will be appended to a list and this
    list is merged to the dictionary in the form: {nodeName:list}.
        - else, nodeToDic() will call itself recursively on
    the nodes children (merging {nodeName:nodeToDic()} to
    the dictionary).
    """
    dic = {}
    for n in node.childNodes:
        if n.nodeType != n.ELEMENT_NODE:
            continue
        if n.getAttribute("multiple") == "true":
            # node with multiple children:
            # put them in a list
            l = []
            for c in n.childNodes:
                if c.nodeType != n.ELEMENT_NODE:
                    continue
                l.append(nodeToDic(c))
                dic.update({n.nodeName:l})
            continue

        try:
            text = getTextFromNode(n)
        except NotTextNodeError:
            # 'normal' node
            dic.update({n.nodeName:nodeToDic(n)})
            continue

        # text node
        dic.update({n.nodeName:text})
        continue
    return dic

