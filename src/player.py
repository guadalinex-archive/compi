# -*- coding: utf-8 -*-

import os
import socket
import codecs
import config
import time
try:
    import pymedia
    pymedia_installed = True
except:
    print "Download Pyplayer from http://sourceforge.net/project/showfiles.php?group_id=86491&package_id=89813&release_id=368116 and use python2.4"
    pymedia_installed = False

_ = config._

class Player:

    def __init__(self, host="localhost", port=1314):
        self.host = host
        self.port = port
        self.socket = None
        global pymedia_installed
        self.pymedia_installed = pymedia_installed

    def run_festival(self):
        try:
            print "Arrancando sintetizador de voces festival en modo servidor..."
            os.execv("/usr/bin/festival", ["festival", "--server"])
        except:
            print "Error al inicar el servidor de voces"
            return 1
        
    def connect(self):
        time.sleep(2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Conectando con el servidor festival (%s:%s)..." % (self.host, self.port)
        try:
            self.socket.connect((self.host, self.port))
        except:
            print "Fallo al conectar con el servidor de voz"
        return self.socket
        
    def play_audio(self, file):
        
        if not self.pymedia_installed:
            return "Pymedia not installed"
        elif os.path.exists(file):
            i = 0
            while i < 5:
                try:
                    dsp = open("/dev/dsp",'w')
                except:
                    print ("Intento %d: Dispositivo de sonido ocupado" % i)
                    time.sleep(1)
                    i += 1
                else:
                    dsp.close()
                    try:
                        print "\tIniciando PyMedia..."
                        player = pymedia.Player()
                        player.start()
                        print "\tCargando archivo '%s'..." % os.path.split(file)[1]
                        player.startPlayback(file)
                        #duracion = player.getLength()
                        while player.isPlaying():
                            time.sleep( 0.01 )
                        i = 7
                    except:
                        print "No se pudo iniciar Pymedia\n"
                        player.stopPlayback()
                    else:
                        print "OK\n"
            if i == 6:
                print ("No fue posible acceder al dispositivo de audio '/dev/dsp'.")
                print ("Compruebe que no haya otro programa haciendo uso de él.")

    def read_text(self, text):
        try:
            text.decode("utf-8").encode("iso-8859-15")
        except:
            print "El texto seleccionado contiene caracteres no válidos"
        text = text.replace("\"", "\\\"")
        data = None
        try:
            if len(text) > 1:
                self.socket.send("(SayText \"%s\")" % text.decode("utf-8").encode("iso-8859-15"))
                while not data:
                    data = self.socket.recv(1024)
                time.sleep(0.2*text.count(' ')+0.3*text.count(',')+0.4*text.count('.'))
        except:
            print "No fue posible hacer la petición al servidor de voces"
        
