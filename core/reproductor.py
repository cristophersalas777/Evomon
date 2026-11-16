import time
import threading
import pyautogui
from pynput.keyboard import Controller as KeyController, Key
from pynput.mouse import Controller as MouseController, Button

pyautogui.FAILSAFE = False

class Reproductor:
    def __init__(self):
        self._activo = False
        self._pausado = False
        self._hilo = None
        self._teclado = KeyController()
        self._mouse = MouseController()

    def iniciar(self, acciones, respawn_segundos, callback_ciclo=None):
        self._activo = True
        self._pausado = False
        self._hilo = threading.Thread(
            target=self._bucle,
            args=(acciones, respawn_segundos, callback_ciclo),
            daemon=True
        )
        self._hilo.start()

    def pausar(self):
        self._pausado = not self._pausado

    def detener(self):
        self._activo = False
        self._pausado = False

    def esta_activo(self):
        return self._activo

    def _bucle(self, acciones, respawn_segundos, callback_ciclo):
        primer_ciclo = True
        while self._activo:
            # Primer ciclo: ejecutar de inmediato sin esperar
            if not primer_ciclo:
                for _ in range(int(respawn_segundos * 10)):
                    if not self._activo:
                        return
                    while self._pausado:
                        time.sleep(0.1)
                    time.sleep(0.1)

            primer_ciclo = False

            if not self._activo:
                return

            # Ejecutar secuencia
            self._ejecutar_secuencia(acciones)

            if callback_ciclo:
                callback_ciclo()

    def _ejecutar_secuencia(self, acciones):
        tiempo_anterior = 0
        for accion in acciones:
            if not self._activo:
                return
            while self._pausado:
                time.sleep(0.1)

            delay = accion["delay"] - tiempo_anterior
            if delay > 0:
                time.sleep(delay)
            tiempo_anterior = accion["delay"]

            tipo = accion["tipo"]

            if tipo == "clic":
                boton = Button.left if "left" in accion["boton"] else Button.right
                self._mouse.position = (accion["x"], accion["y"])
                time.sleep(0.05)
                self._mouse.click(boton)

            elif tipo == "tecla":
                tecla_str = accion["tecla"]
                try:
                    if tecla_str.startswith("Key."):
                        nombre = tecla_str.replace("Key.", "")
                        tecla = getattr(Key, nombre)
                        self._teclado.press(tecla)
                        self._teclado.release(tecla)
                    else:
                        self._teclado.press(tecla_str)
                        self._teclado.release(tecla_str)
                except Exception:
                    pass

            elif tipo == "scroll":
                self._mouse.position = (accion["x"], accion["y"])
                self._mouse.scroll(accion["dx"], accion["dy"])
