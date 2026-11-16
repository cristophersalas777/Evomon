"""
Evomon - Macro App para Roblox
Autor: Cebollin
"""

import customtkinter as ctk
import tkinter as tk
import threading
import time
import os
from tkinter import messagebox, simpledialog
from core.grabador import Grabador
from core.reproductor import Reproductor
from core.gestor_perfiles import guardar_perfil, cargar_perfil, listar_perfiles, eliminar_perfil, cargar_ultimo_perfil, guardar_ultimo_perfil
from pynput import keyboard as pynput_keyboard
from PIL import Image, ImageTk

BG       = "#1e2130"
SURFACE  = "#252a3a"
SURFACE2 = "#2e3450"
ACCENT   = "#6c63ff"
VERDE    = "#00c896"
ROJO     = "#ff5370"
AMARILLO = "#ffcb6b"
TEXTO    = "#e0e6f0"
SUBTEXTO = "#7a85a0"

# Teclas por defecto
_D_INICIAR      = "F6"
_D_DETENER      = "F7"
_D_GRABAR       = "F8"
_D_PARAR_GRABAR = "F9"


def _nombre_tecla(key):
    try:
        c = key.char
        return c.upper() if c else str(key).replace("Key.", "").upper()
    except AttributeError:
        return str(key).replace("Key.", "").upper()


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Evomon")
        self.geometry("460x640")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.attributes("-topmost", True)

        self._grabador    = Grabador()
        self._reproductor = Reproductor()
        self._acciones_actuales = []
        self._corriendo  = False
        self._grabando   = False
        self._ciclos     = 0

        self._tecla_iniciar      = _D_INICIAR
        self._tecla_detener      = _D_DETENER
        self._tecla_grabar       = _D_GRABAR
        self._tecla_parar_grabar = _D_PARAR_GRABAR
        self._esperando_tecla    = None

        self._construir_ui()
        self._actualizar_lista_perfiles()
        self._registrar_teclas_globales()

    # ═══════════════════════════ UI ═══════════════════════════════

    def _construir_ui(self):

        # ── HEADER
        hdr = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Logo desde imagen real (sin fondo)
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "pokebola_sin_fondo.png")
        pil_logo = Image.open(logo_path).resize((36, 36), Image.LANCZOS)
        self._logo_img = ImageTk.PhotoImage(pil_logo)
        lbl_logo = tk.Label(hdr, image=self._logo_img, bg=SURFACE, bd=0)
        lbl_logo.place(x=10, rely=0.5, anchor="w")

        ctk.CTkLabel(hdr, text="Evomon",
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXTO).place(x=52, rely=0.5, anchor="w")
        ctk.CTkLabel(hdr, text="by Cebollin",
                     font=("Segoe UI", 9), text_color=SUBTEXTO
                     ).place(x=132, rely=0.5, anchor="w")
        self._badge = ctk.CTkLabel(
            hdr, text="● Inactivo",
            font=("Segoe UI", 10, "bold"), text_color=SUBTEXTO,
            fg_color=SURFACE2, corner_radius=20, padx=10, pady=2)
        self._badge.place(relx=1.0, x=-12, rely=0.5, anchor="e")

        # ── PERFIL
        sec_p = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10)
        sec_p.pack(fill="x", padx=16, pady=(10, 4))

        # Fila nombre del perfil (editable directamente)
        row_nombre = ctk.CTkFrame(sec_p, fg_color="transparent")
        row_nombre.pack(fill="x", padx=12, pady=(8, 3))
        ctk.CTkLabel(row_nombre, text="Nombre",
                     font=("Segoe UI", 10), text_color=SUBTEXTO,
                     width=58).pack(side="left")
        self._entry_nombre = ctk.CTkEntry(
            row_nombre, width=270, height=30,
            fg_color=SURFACE2, border_color=SURFACE2,
            font=("Segoe UI", 10), text_color=TEXTO,
            placeholder_text="Nombre del Evomon...")
        self._entry_nombre.pack(side="left", padx=4)
        self._entry_nombre.bind("<KeyRelease>", lambda e: self._actualizar_btn_guardar())

        # Fila cargar perfil guardado
        row_cargar = ctk.CTkFrame(sec_p, fg_color="transparent")
        row_cargar.pack(fill="x", padx=12, pady=(0, 3))
        ctk.CTkLabel(row_cargar, text="Cargar",
                     font=("Segoe UI", 10), text_color=SUBTEXTO,
                     width=58).pack(side="left")

        self._frame_dropdown = ctk.CTkFrame(row_cargar, fg_color=SURFACE2, corner_radius=8, width=270, height=30)
        self._frame_dropdown.pack(side="left", padx=4)
        self._frame_dropdown.pack_propagate(False)

        self._lbl_perfil_sel = ctk.CTkLabel(
            self._frame_dropdown, text="-- Sin perfiles --",
            font=("Segoe UI", 10), text_color=TEXTO, anchor="w")
        self._lbl_perfil_sel.place(x=10, rely=0.5, anchor="w")

        btn_drop = ctk.CTkButton(
            self._frame_dropdown, text="▾", width=26, height=24,
            fg_color=ACCENT, hover_color="#5a52d5",
            font=("Segoe UI", 11, "bold"),
            corner_radius=6, command=self._toggle_dropdown)
        btn_drop.place(relx=1.0, x=-3, rely=0.5, anchor="e")

        self._popup_dropdown = None
        self._dropdown_cerrado_en = 0.0

        # Fila respawn
        row_resp = ctk.CTkFrame(sec_p, fg_color="transparent")
        row_resp.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(row_resp, text="Respawn",
                     font=("Segoe UI", 10), text_color=SUBTEXTO,
                     width=70).pack(side="left")

        col_min = ctk.CTkFrame(row_resp, fg_color="transparent")
        col_min.pack(side="left", padx=(8, 2))
        ctk.CTkLabel(col_min, text="minutos",
                     font=("Segoe UI", 8), text_color=SUBTEXTO).pack()
        self._entry_minutos = ctk.CTkEntry(
            col_min, width=66, height=30,
            fg_color=SURFACE2, border_color=SURFACE2,
            font=("Segoe UI", 12, "bold"), justify="center")
        self._entry_minutos.pack()

        ctk.CTkLabel(row_resp, text=":",
                     font=("Segoe UI", 16, "bold"), text_color=ACCENT
                     ).pack(side="left", padx=5)

        col_seg = ctk.CTkFrame(row_resp, fg_color="transparent")
        col_seg.pack(side="left", padx=(2, 0))
        ctk.CTkLabel(col_seg, text="segundos",
                     font=("Segoe UI", 8), text_color=SUBTEXTO).pack()
        self._entry_segundos = ctk.CTkEntry(
            col_seg, width=66, height=30,
            fg_color=SURFACE2, border_color=SURFACE2,
            font=("Segoe UI", 12, "bold"), justify="center")
        self._entry_segundos.pack()

        # ── BARRA ESTADO / COUNTDOWN
        barra = ctk.CTkFrame(self, fg_color=SURFACE2, height=34, corner_radius=8)
        barra.pack(fill="x", padx=16, pady=(0, 4))
        barra.pack_propagate(False)

        self._lbl_fase = ctk.CTkLabel(
            barra, text="",
            font=("Segoe UI", 9), text_color=SUBTEXTO)
        self._lbl_fase.place(x=12, rely=0.5, anchor="w")

        self._lbl_countdown = ctk.CTkLabel(
            barra, text="--:--",
            font=("Segoe UI", 13, "bold"), text_color=ACCENT)
        self._lbl_countdown.place(relx=0.5, rely=0.5, anchor="center")

        self._lbl_ciclos = ctk.CTkLabel(
            barra, text="Ciclos: 0",
            font=("Segoe UI", 9), text_color=SUBTEXTO)
        self._lbl_ciclos.place(relx=1.0, x=-12, rely=0.5, anchor="e")

        # ── CONTROL
        sec_ctrl = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10)
        sec_ctrl.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(sec_ctrl, text="CONTROL",
                     font=("Segoe UI", 8, "bold"), text_color=SUBTEXTO
                     ).pack(anchor="w", padx=12, pady=(6, 3))

        row_ctrl = ctk.CTkFrame(sec_ctrl, fg_color="transparent")
        row_ctrl.pack(padx=10, pady=(0, 8))

        self._btn_iniciar = ctk.CTkButton(
            row_ctrl, text=f"▶  Iniciar  [{self._tecla_iniciar}]",
            width=206, height=36, corner_radius=8,
            fg_color=VERDE, hover_color="#00a87d", text_color="#0d1f1a",
            font=("Segoe UI", 10, "bold"), command=self._iniciar)
        self._btn_iniciar.pack(side="left", padx=4)

        self._btn_detener = ctk.CTkButton(
            row_ctrl, text=f"■  Detener  [{self._tecla_detener}]",
            width=206, height=36, corner_radius=8,
            fg_color=ROJO, hover_color="#d9405a",
            font=("Segoe UI", 10, "bold"), command=self._detener,
            state="disabled")
        self._btn_detener.pack(side="left", padx=4)

        # ── GRABACIÓN
        sec_grab = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10)
        sec_grab.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(sec_grab, text="GRABACIÓN",
                     font=("Segoe UI", 8, "bold"), text_color=SUBTEXTO
                     ).pack(anchor="w", padx=12, pady=(6, 3))

        row_grab = ctk.CTkFrame(sec_grab, fg_color="transparent")
        row_grab.pack(padx=10, pady=(0, 8))

        self._btn_grabar = ctk.CTkButton(
            row_grab, text=f"⏺  Grabar  [{self._tecla_grabar}]",
            width=206, height=36, corner_radius=8,
            fg_color=ACCENT, hover_color="#5a52d5",
            font=("Segoe UI", 10, "bold"), command=self._grabar)
        self._btn_grabar.pack(side="left", padx=4)

        self._btn_parar_grabar = ctk.CTkButton(
            row_grab, text=f"⏹  Parar  [{self._tecla_parar_grabar}]",
            width=206, height=36, corner_radius=8,
            fg_color=SURFACE2, hover_color=BG,
            font=("Segoe UI", 10, "bold"),
            command=self._parar_grabacion, state="disabled")
        self._btn_parar_grabar.pack(side="left", padx=4)

        # ── INFO ACCIONES
        self._lbl_acciones = ctk.CTkLabel(
            self, text="Sin secuencia grabada",
            font=("Segoe UI", 9), text_color=SUBTEXTO)
        self._lbl_acciones.pack(pady=(2, 3))

        # ── PERFILES
        row_prf = ctk.CTkFrame(self, fg_color="transparent")
        row_prf.pack(fill="x", padx=16, pady=(0, 4))

        self._btn_guardar = ctk.CTkButton(
            row_prf, text="💾  Guardar perfil",
                      width=206, height=32, corner_radius=8,
                      fg_color=SURFACE, hover_color=SURFACE2,
                      border_width=1, border_color=VERDE, text_color=VERDE,
                      font=("Segoe UI", 10), command=self._guardar_perfil
                      )
        self._btn_guardar.pack(side="left", padx=4)

        ctk.CTkButton(row_prf, text="🗑  Eliminar perfil",
                      width=206, height=32, corner_radius=8,
                      fg_color=SURFACE, hover_color=SURFACE2,
                      border_width=1, border_color=ROJO, text_color=ROJO,
                      font=("Segoe UI", 10), command=self._eliminar_perfil
                      ).pack(side="left", padx=4)

        # ── TECLAS CONFIGURABLES
        sec_keys = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10)
        sec_keys.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(sec_keys,
                     text="⌨  TECLAS RÁPIDAS  —  clic y presiona la tecla",
                     font=("Segoe UI", 8, "bold"), text_color=SUBTEXTO
                     ).pack(anchor="w", padx=12, pady=(6, 3))

        row_keys = ctk.CTkFrame(sec_keys, fg_color="transparent")
        row_keys.pack(padx=8, pady=(0, 6))

        self._btn_ak_iniciar = self._key_btn(
            row_keys, f"▶ {self._tecla_iniciar}", VERDE,
            lambda: self._esperar_tecla("iniciar"))
        self._btn_ak_iniciar.pack(side="left", padx=3)

        self._btn_ak_detener = self._key_btn(
            row_keys, f"■ {self._tecla_detener}", ROJO,
            lambda: self._esperar_tecla("detener"))
        self._btn_ak_detener.pack(side="left", padx=3)

        self._btn_ak_grabar = self._key_btn(
            row_keys, f"⏺ {self._tecla_grabar}", ACCENT,
            lambda: self._esperar_tecla("grabar"))
        self._btn_ak_grabar.pack(side="left", padx=3)

        self._btn_ak_parar = self._key_btn(
            row_keys, f"⏹ {self._tecla_parar_grabar}", AMARILLO,
            lambda: self._esperar_tecla("parar_grabar"))
        self._btn_ak_parar.pack(side="left", padx=3)

        self._lbl_tecla_hint = ctk.CTkLabel(
            sec_keys, text="",
            font=("Segoe UI", 9), text_color=SUBTEXTO)
        self._lbl_tecla_hint.pack(pady=(0, 8))

    def _toggle_dropdown(self):
        ahora = time.time()
        if self._dropdown_cerrado_en and ahora - self._dropdown_cerrado_en < 0.25:
            return

        if self._popup_dropdown is not None:
            try:
                if self._popup_dropdown.winfo_exists():
                    self._popup_dropdown.destroy()
            except Exception:
                pass
            self._popup_dropdown = None
            self._dropdown_cerrado_en = time.time()
            return

        perfiles = listar_perfiles()
        if not perfiles:
            return

        self._frame_dropdown.update_idletasks()
        x     = self._frame_dropdown.winfo_rootx()
        y     = self._frame_dropdown.winfo_rooty() + self._frame_dropdown.winfo_height()
        ancho = self._frame_dropdown.winfo_width()

        BG_POPUP = "#3d4466"
        BG_HOVER = "#6c63ff"
        FG_TEXT  = "#e0e6f0"
        FG_HOVER = "#ffffff"
        RADIO    = 10

        alto_item = 28
        pad       = 6
        total_h   = len(perfiles) * alto_item + pad * 2

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg=BG_POPUP)
        popup.geometry(f"{ancho}x{total_h}+{x}+{y}")

        canvas = tk.Canvas(popup, width=ancho, height=total_h,
                           bg=BG_POPUP, highlightthickness=0)
        canvas.place(x=0, y=0)

        def _rounded_rect(c, x1, y1, x2, y2, r, **kw):
            c.create_arc(x1,     y1,     x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kw)
            c.create_arc(x2-2*r, y1,     x2,     y1+2*r, start=0,   extent=90,  style="pieslice", **kw)
            c.create_arc(x1,     y2-2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", **kw)
            c.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90,  style="pieslice", **kw)
            c.create_rectangle(x1+r, y1,     x2-r, y2,     **kw)
            c.create_rectangle(x1,   y1+r,   x2,   y2-r,   **kw)

        _rounded_rect(canvas, 0, 0, ancho, total_h, RADIO,
                      fill=BG_POPUP, outline=BG_POPUP)
        canvas.create_rectangle(0, 0, ancho, RADIO, fill=BG_POPUP, outline=BG_POPUP)

        def _cerrar():
            self._popup_dropdown = None
            self._dropdown_cerrado_en = time.time()
            try:
                popup.destroy()
            except Exception:
                pass

        for i, nombre in enumerate(perfiles):
            iy = pad + i * alto_item

            def hacer_cmd(n=nombre):
                _cerrar()
                self._on_seleccionar_perfil(n)

            rect_id = canvas.create_rectangle(
                4, iy, ancho - 4, iy + alto_item - 2,
                fill=BG_POPUP, outline=BG_POPUP)

            lbl = tk.Label(popup, text=f"  {nombre}",
                           bg=BG_POPUP, fg=FG_TEXT,
                           font=("Segoe UI", 9), anchor="w",
                           cursor="hand2")
            lbl.place(x=4, y=iy, width=ancho - 8, height=alto_item - 2)

            def on_enter(e, r=rect_id, l=lbl):
                canvas.itemconfig(r, fill=BG_HOVER, outline=BG_HOVER)
                l.configure(bg=BG_HOVER, fg=FG_HOVER)
            def on_leave(e, r=rect_id, l=lbl):
                canvas.itemconfig(r, fill=BG_POPUP, outline=BG_POPUP)
                l.configure(bg=BG_POPUP, fg=FG_TEXT)

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e, cmd=hacer_cmd: cmd())

        popup.bind("<FocusOut>", lambda e: _cerrar())
        popup.focus_set()
        self._popup_dropdown = popup

    def _set_dropdown_texto(self, texto):
        self._lbl_perfil_sel.configure(text=texto)

    def _key_btn(self, parent, txt, color, cmd):
        return ctk.CTkButton(
            parent, text=txt, width=86, height=28, corner_radius=6,
            fg_color=SURFACE2, hover_color=BG,
            border_width=1, border_color=color,
            text_color=color, font=("Segoe UI", 9, "bold"),
            command=cmd)

    # ═══════════════════════ LÓGICA ═══════════════════════════════

    def _on_seleccionar_perfil(self, nombre):
        if nombre.startswith("--"):
            return
        datos = cargar_perfil(nombre)
        if datos:
            self._acciones_actuales = datos.get("acciones", [])
            self._entry_nombre.delete(0, "end")
            self._entry_nombre.insert(0, nombre)
            self._entry_minutos.delete(0, "end")
            self._entry_minutos.insert(0, str(datos.get("respawn_minutos", 0)))
            self._entry_segundos.delete(0, "end")
            self._entry_segundos.insert(0, str(datos.get("respawn_segundos", 0)))
            self._lbl_acciones.configure(
                text=f"✓  {len(self._acciones_actuales)} acciones  •  perfil '{nombre}'",
                text_color=VERDE)
            self._set_dropdown_texto(nombre)
            guardar_ultimo_perfil(nombre)
            self._actualizar_btn_guardar(nombre)

    def _iniciar(self):
        if not self._acciones_actuales:
            messagebox.showwarning("Sin secuencia", "Primero graba una secuencia.")
            return
        try:
            mins = int(self._entry_minutos.get() or 0)
            segs = int(self._entry_segundos.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "El tiempo debe ser un número.")
            return
        total = mins * 60 + segs
        self._corriendo = True
        self._ciclos    = 0
        self._btn_iniciar.configure(state="disabled")
        self._btn_detener.configure(state="normal")
        self._btn_grabar.configure(state="disabled")
        self._set_badge("Corriendo", VERDE)
        self._reproductor.iniciar(
            self._acciones_actuales, total,
            callback_ciclo=self._on_ciclo_completado)
        self._iniciar_countdown(total)

    def _iniciar_countdown(self, total):
        def tick():
            # Fase 1: ejecutando secuencia
            self.after(0, lambda: self._lbl_fase.configure(
                text="Ejecutando...", text_color=AMARILLO))
            self.after(0, lambda: self._lbl_countdown.configure(text="⚡"))

            # Esperar duración real de la secuencia
            dur = (self._acciones_actuales[-1]["delay"] + 0.5
                   if self._acciones_actuales else 0)
            tiempo_inicio = time.time()
            while self._corriendo and (time.time() - tiempo_inicio) < dur:
                time.sleep(0.05)

            # Fase 2: countdown preciso con time.time()
            while self._corriendo:
                self.after(0, lambda: self._lbl_fase.configure(
                    text="Esperando respawn...", text_color=SUBTEXTO))

                t_ciclo = time.time()
                while self._corriendo:
                    transcurrido = time.time() - t_ciclo
                    restante = max(0, total - transcurrido)
                    m, s = divmod(int(restante), 60)
                    self.after(0, lambda m=m, s=s:
                               self._lbl_countdown.configure(text=f"{m:02d}:{s:02d}"))
                    if restante <= 0:
                        break
                    time.sleep(0.25)   # actualiza 4 veces por segundo, ligero

                if not self._corriendo:
                    break

                # Nuevo ciclo
                self.after(0, lambda: self._lbl_fase.configure(
                    text="Ejecutando...", text_color=AMARILLO))
                self.after(0, lambda: self._lbl_countdown.configure(text="⚡"))
                t_exec = time.time()
                while self._corriendo and (time.time() - t_exec) < dur:
                    time.sleep(0.05)

            self.after(0, lambda: self._lbl_countdown.configure(text="--:--"))
            self.after(0, lambda: self._lbl_fase.configure(text=""))

        threading.Thread(target=tick, daemon=True).start()

    def _on_ciclo_completado(self):
        self._ciclos += 1
        self.after(0, lambda: self._lbl_ciclos.configure(text=f"Ciclos: {self._ciclos}"))

    def _detener(self):
        self._corriendo = False
        self._reproductor.detener()
        self._btn_iniciar.configure(state="normal")
        self._btn_detener.configure(state="disabled")
        self._btn_grabar.configure(state="normal")
        self._lbl_countdown.configure(text="--:--")
        self._lbl_fase.configure(text="")
        self._set_badge("Detenido", ROJO)

    def _set_badge(self, texto, color):
        self._badge.configure(text=f"● {texto}", text_color=color)

    def _grabar(self):
        self._acciones_actuales = []   # borra acciones anteriores
        self._grabando = True
        self._grabador.iniciar()
        self._btn_grabar.configure(state="disabled")
        self._btn_parar_grabar.configure(state="normal")
        self._btn_iniciar.configure(state="disabled")
        self._set_badge("Grabando...", AMARILLO)
        self._lbl_acciones.configure(
            text="● Grabando acciones...", text_color=AMARILLO)

    def _parar_grabacion(self):
        acciones = self._grabador.detener()
        self._grabando = False
        self._acciones_actuales = acciones
        self._btn_grabar.configure(state="normal")
        self._btn_parar_grabar.configure(state="disabled")
        self._btn_iniciar.configure(state="normal")
        self._set_badge("Listo", VERDE)
        self._lbl_acciones.configure(
            text=f"✓  {len(acciones)} acciones grabadas  •  Listo para iniciar",
            text_color=VERDE)

    def _combo_perfiles_set(self, nombre):
        self._lbl_perfil_sel.configure(text=nombre)

    def _actualizar_btn_guardar(self, nombre_actual=None):
        """Cambia el texto del botón guardar según si el perfil ya existe.
        Usa caché local para no leer el disco en cada KeyRelease."""
        if nombre_actual is None:
            nombre_actual = self._entry_nombre.get().strip()
        # Solo lee disco si el nombre cambió desde la última vez
        if nombre_actual != getattr(self, "_ultimo_nombre_check", None):
            self._ultimo_nombre_check = nombre_actual
            self._nombre_existe_cache = nombre_actual in listar_perfiles()
        if nombre_actual and self._nombre_existe_cache:
            self._btn_guardar.configure(text="💾  Actualizar perfil")
        else:
            self._btn_guardar.configure(text="💾  Guardar perfil")

    def _guardar_perfil(self):
        nombre = self._entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Sin nombre", "Escribe el nombre del Evomon en el campo 'Nombre'.")
            return
        if not self._acciones_actuales:
            messagebox.showwarning("Sin secuencia", "Graba una secuencia antes de guardar.")
            return
        try:
            mins = int(self._entry_minutos.get() or 0)
            segs = int(self._entry_segundos.get() or 0)
        except ValueError:
            mins, segs = 0, 0

        es_nuevo = nombre not in listar_perfiles()
        guardar_perfil(nombre, mins, segs, self._acciones_actuales)
        # Invalidar caché
        self._ultimo_nombre_check = None
        self._actualizar_lista_perfiles()
        self._combo_perfiles_set(nombre)

        accion = "creado" if es_nuevo else "actualizado"
        self._lbl_acciones.configure(
            text=f"✓  Perfil '{nombre}' {accion}  •  {len(self._acciones_actuales)} acciones",
            text_color=VERDE)
        self._actualizar_btn_guardar(nombre)

    def _eliminar_perfil(self):
        nombre = self._entry_nombre.get().strip()
        if not nombre:
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar el perfil '{nombre}'?"):
            eliminar_perfil(nombre)
            self._acciones_actuales = []
            self._entry_nombre.delete(0, "end")
            self._actualizar_lista_perfiles()
            self._lbl_acciones.configure(text="Perfil eliminado", text_color=SUBTEXTO)

    def _actualizar_lista_perfiles(self):
        perfiles = listar_perfiles()
        if perfiles:
            ultimo = cargar_ultimo_perfil()
            if ultimo and ultimo in perfiles:
                self._set_dropdown_texto(ultimo)
                self._on_seleccionar_perfil(ultimo)
            else:
                self._set_dropdown_texto(perfiles[0])
                self._on_seleccionar_perfil(perfiles[0])
        else:
            self._set_dropdown_texto("-- Sin perfiles guardados --")

    # ═══════════════ TECLAS CONFIGURABLES ═════════════════════════

    def _esperar_tecla(self, accion):
        self._esperando_tecla = accion
        nombres = {
            "iniciar": "Iniciar",
            "detener": "Detener",
            "grabar": "Grabar",
            "parar_grabar": "Parar Grabación"
        }
        self._lbl_tecla_hint.configure(
            text=f"Presiona la tecla para '{nombres[accion]}'...",
            text_color=AMARILLO)

    def _aplicar_nueva_tecla(self, accion, nombre):
        self._esperando_tecla = None
        if accion == "iniciar":
            self._tecla_iniciar = nombre
            self._btn_iniciar.configure(text=f"▶  Iniciar  [{nombre}]")
            self._btn_ak_iniciar.configure(text=f"▶ {nombre}")
        elif accion == "detener":
            self._tecla_detener = nombre
            self._btn_detener.configure(text=f"■  Detener  [{nombre}]")
            self._btn_ak_detener.configure(text=f"■ {nombre}")
        elif accion == "grabar":
            self._tecla_grabar = nombre
            self._btn_grabar.configure(text=f"⏺  Grabar  [{nombre}]")
            self._btn_ak_grabar.configure(text=f"⏺ {nombre}")
        elif accion == "parar_grabar":
            self._tecla_parar_grabar = nombre
            self._btn_parar_grabar.configure(text=f"⏹  Parar  [{nombre}]")
            self._btn_ak_parar.configure(text=f"⏹ {nombre}")
        self._lbl_tecla_hint.configure(
            text=f"✓  '{nombre}' asignada a {accion}",
            text_color=VERDE)

    # ═══════════════ LISTENER GLOBAL ══════════════════════════════

    def _registrar_teclas_globales(self):
        def on_press(key):
            nombre = _nombre_tecla(key)
            if self._esperando_tecla is not None:
                accion = self._esperando_tecla
                self._esperando_tecla = None
                self.after(0, lambda: self._aplicar_nueva_tecla(accion, nombre))
                return
            if nombre == self._tecla_iniciar and not self._corriendo and not self._grabando:
                self.after(0, self._iniciar)
            elif nombre == self._tecla_detener and self._corriendo:
                self.after(0, self._detener)
            elif nombre == self._tecla_grabar and not self._corriendo and not self._grabando:
                self.after(0, self._grabar)
            elif nombre == self._tecla_parar_grabar and self._grabando:
                self.after(0, self._parar_grabacion)

        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
