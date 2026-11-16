import threading
import time

class Timer:
    def __init__(self, callback_tick=None, callback_fin=None):
        self._callback_tick = callback_tick
        self._callback_fin = callback_fin
        self._hilo = None
        self._activo = False

    def iniciar(self, segundos_totales):
        self._activo = True
        self._hilo = threading.Thread(
            target=self._correr,
            args=(segundos_totales,),
            daemon=True
        )
        self._hilo.start()

    def detener(self):
        self._activo = False

    def _correr(self, segundos_totales):
        restante = segundos_totales
        while restante > 0 and self._activo:
            if self._callback_tick:
                self._callback_tick(restante)
            time.sleep(1)
            restante -= 1
        if self._activo and self._callback_fin:
            self._callback_fin()
