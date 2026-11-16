import customtkinter as ctk
from ui.ventana import VentanaPrincipal

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = VentanaPrincipal()
    app.mainloop()
