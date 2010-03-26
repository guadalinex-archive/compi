# -*- coding: utf-8 -*-

import os
import socket
import codecs
import config
import time
import pygame

_ = config._

class Player:

    def __init__(self, host="localhost", port=1314):
        self.host = host
        self.port = port
        self.socket = None



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
        if os.path.exists(file):
            try:
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            except:
                print "Fallo al repoducir el archivo %s" % file
       
    def stop_audio(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            print "Fallo detener la reproduccion"

    def read_text(self, text):
        try:
            text.decode("utf-8").encode("iso-8859-15")
        except:
            print "El texto seleccionado contiene caracteres no válidos"
        text = text.replace("\"", "\\\"")
        data = None
        try:
            if len(text) > 1:
                self.stop_audio()
                self.socket.send("(SayText \"%s\")" % text.decode("utf-8").encode("iso-8859-15"))
                while not data:
                    data = self.socket.recv(1024)
                time.sleep(0.2*text.count(' ')+0.3*text.count(',')+0.4*text.count('.'))
        except:
            print "No fue posible hacer la petición al servidor de voces"
        
