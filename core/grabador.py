import time
import json
from pynput import mouse, keyboard

class Grabador:
    def __init__(self):
        self.acciones = []
        self.grabando = False
        self._tiempo_inicio = None
        self._mouse_listener = None
        self._keyboard_listener = None

    def iniciar(self):
        self.acciones = []
        self.grabando = True
        self._tiempo_inicio = time.time()

        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_press
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def detener(self):
        self.grabando = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        return self.acciones

    def _tiempo_actual(self):
        return round(time.time() - self._tiempo_inicio, 3)

    def _on_click(self, x, y, button, pressed):
        if self.grabando and pressed:
            self.acciones.append({
                "tipo": "clic",
                "x": x,
                "y": y,
                "boton": str(button),
                "delay": self._tiempo_actual()
            })

    def _on_scroll(self, x, y, dx, dy):
        if self.grabando:
            self.acciones.append({
                "tipo": "scroll",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "delay": self._tiempo_actual()
            })

    def _on_press(self, key):
        if self.grabando:
            try:
                tecla = key.char
            except AttributeError:
                tecla = str(key)
            self.acciones.append({
                "tipo": "tecla",
                "tecla": tecla,
                "delay": self._tiempo_actual()
            })
