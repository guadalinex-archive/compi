# -*- coding: utf-8 -*-

import os
import socket
import codecs
import config
import time
import pygame
import subprocess

_ = config._

class Player:

    def __init__(self, host="localhost", port=1314):
        self.host = host
        self.port = port
        self.fest = None
        self.socket = None

    def run_festival(self):
        try:
            print "Arrancando sintetizador de voces festival en modo servidor..."
            self.fest = subprocess.Popen(["/usr/bin/festival", "--server"])
        except:
            print "Error al inicar el servidor de voces"
            return 1
        
    def stop_festival(self):
        try:
            print "Deteniendo sintetizador de voces festival..."
            self.stop_audio()
            self.fest.terminate()
            self.fest.wait()
        except:
            print "Error al detener el servidor de voces"
            return 1
            
    def set_voice(self, voice):
        data = None
        try:
            self.socket.send("(%s)" % voice)
            while not data:
                data = self.socket.recv(1024)
                print data
            time.sleep(0.1)
        except:
            print "No fue posible hacer la petición al servidor de voces"
            
    def connect(self):
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
                pygame.mixer.init()
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            except:
                print "Fallo al repoducir el archivo %s" % file
       
    def stop_audio(self):
        try:
            #pygame.mixer.music.stop()
            pygame.mixer.quit()
            time.sleep(1.0)
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
        
