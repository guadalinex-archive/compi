# -*- coding: utf-8 -*-

from threading import Thread
from threading import Event
from time import sleep
import os
from Xlib import X

# Objeto que representa al puntero del raton y las
# operaciones que haremos sobre el
class Mouse(Thread):

    def __init__(self):
        Thread.__init__(self)
        self._stopevent = Event()
        try:
            from Xlib import display
            from Xlib import X
            import xmouse # wrapper de la funcion en C XTestFakeButton
            self.click = xmouse.click
        except:
            return 0
        ENV_DISPLAY = os.environ.get("DISPLAY")
        try:
            self.display = display.Display(ENV_DISPLAY )
        except:
            print "Fallo de Xlib. Posible incompatibilidad con el actual driver NVIDIA"
            return 0
            
        self.screen = self.display.screen()
        # Anchura y altura de la pantalla
        self.w = int( self.screen['width_in_pixels'] )
        self.h = int( self.screen['height_in_pixels'] )

        self.return_origin = True
        self.progresivo = False
        self.ralentizacion = 0.5
        self.wait_clic = 0
        # Inicio del movimiento
        self.x , self.y = 0, 0

        # Numero de pixels que en que el sistema avanzara
        self.avance = 4
        self.direccion = True
        # tiempo de espera entre dos acciones
        self.espera = 0.02
        # accion por defecto del ratón
        self.action = None
        # lista de posiciones almacenadas
        self.posiciones = []

   # mueve el puntero a las coordenadas especificadas
    def move_to(self, x, y):
        self.screen.root.warp_pointer(x,y)
        self.display.sync()
        self.x, self.y = x, y

    
    def set_slow_speed(self):
        self.avance_normal = self.avance
        self.avance = int(self.ralentizacion * self.avance)
        
        
    def set_normal_speed(self):
        self.avance = self.avance_normal
        
    def set_scroll(self, avance):
        self.avance = avance
        
    def set_time_wait(self, time):
        self.espera = time
        
    def get_position(self):
        pos = self.screen.root.query_pointer()
        #print("%s, %s" % (pos.root_x, pos.root_y))
        return pos.root_x, pos.root_y
          
    def leftClick(self):
        self.click(self.display.get_display_name(),1)

    def rightClick(self):
        self.click(self.display.get_display_name(),3)

    def medClick(self):
        self.click(self.display.get_display_name(),2)
        
    def doubleClick(self):
        leftClick()
        sleep(0.1)
        leftClick()
        
    def move_x(self):
        if self.x >= self.w:
            self.x = 0
            if self.progresivo:
                self.y += self.avance
        elif self.x < 0:
            self.x = self.w
        self.move_to(self.x + self.avance, self.y)

    def move_y(self):        
        if self.y >= self.h:
            self.y = 0
            if self.progresivo:
                self.x += self.avance
        elif self.y < 0:
            self.y = self.h
        self.move_to(self.x, self.y + self.avance)

    def move_pointer(self):
        if self.direccion:
            self.move_y()
        else:
            self.move_x()

    def run(self):
        while not self._stopevent.isSet():
            if self.action == "scan":
                self.check_keys()
                self.move_pointer()
                self._stopevent.wait(self.espera)
            elif self.action == "jump":
                for p in self.posiciones:
                    self.move_to(p[0], p[1])
                    self._stopevent.wait(self.espera)
                    if self.action == "pause": break
            elif self.action == "record":
                self.record_pointer()
                self.action = "pause"
            elif self.action == "pause": 
                self._stopevent.wait(0.25)
                self.check_keys()
            
            else:
                self._stopevent.set()
                print "No se ha especificado ninguna acción"
            
    def record_pointer(self):
        # capturamos los eventos del ratón
        r = self.screen.root.grab_pointer(0, X.ButtonPressMask, X.GrabModeAsync, 
                        X.GrabModeAsync, X.NONE, X.NONE, X.CurrentTime)
        if r == X.GrabSuccess:
            # permitimos los eventos
            self.display.allow_events(X.AsyncBoth|X.ReplayPointer|X.ReplayKeyboard, X.CurrentTime )
            while self.action == "record":
                # esperamos cada evento
                e = self.screen.root.display.next_event()
                #print e
                if e.detail == 1:
                    print "Pulsado boton izquierdo en (%d, %d)" % (e.root_x, e.root_y)
                    self.posiciones.append((e.root_x, e.root_y))
                else:
                    print "Almacenadas %d posiciones" % len(self.posiciones)
                    self.action = "pause"
        self.display.ungrab_pointer(X.CurrentTime)
        self.display.sync()
    
    def grab_keys (self, clic, stop):
        for keycode in (clic, stop):
                self.screen.root.grab_key(keycode, X.AnyModifier, 1,X.GrabModeAsync, X.GrabModeAsync)
        self.clic = clic
        self.stop = stop
        
    def ungrab_keys(self):
        for keycode in (self.clic, self.stop):
            self.screen.root.ungrab_key(keycode, X.AnyModifier)
        self.display.sync()
        
    def check_keys(self):
        if self.display.pending_events():
            event = self.screen.root.display.next_event()
            keycode = event.detail
            if self.action == "pause" and event.type == X.KeyPress and keycode == self.stop:
                self.action = "scan"
                if self.wait_clic:
                     if self.wait_clic == 1:
                         self.leftClick()
                     elif self.wait_clic == 2:
                         selfdoubleClic()
                     elif self.wait_clic == 3:
                         self.rightClick()
                     self.action = "pause"
            elif event.type == X.KeyPress and keycode == self.clic:
                self.set_slow_speed()
            elif event.type == X.KeyRelease and keycode == self.clic:
                self.change_direction()
                self.set_normal_speed()
            elif event.type == X.KeyPress and keycode == self.stop:
                self.action = "pause"

    
    def ungrab_pointer(self):
        self.display.ungrab_pointer(X.CurrentTime)
        self.display.sync()
       
        
    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        Thread.join(self, timeout)

        
    def set_action(self, action):
        self.action = action
                
    def change_direction(self):
        if not self.direccion:
            self.leftClick()
            if self.return_origin:
                self.x, self.y = 0, 0
        self.direccion = not self.direccion
        
        
if __name__ == '__main__':
    m = Mouse()
    m.set_action("scan")
   
    m.start()
    for i in range (5):
        print m.get_position()
        sleep(1)
        m.change_direction()
        sleep(2)
    
    m.join()
