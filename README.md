# ⚔ Evomon
**Macro app de escritorio para Roblox**  
*by CEBOLLIN*

---

## ¿Qué es?
Evomon es una app de escritorio que automatiza el farmeo de monstruos en Roblox. Graba tu secuencia de acciones, configura el tiempo de respawn y deja que la app repita el proceso automáticamente.

## Funciones
- ⏺ Grabar secuencia de acciones (clics + teclado)
- ▶ Reproducir en bucle automático
- ⏱ Timer de respawn configurable (minutos y segundos)
- 💾 Múltiples perfiles guardados por monstruo
- ⌨ Teclas de acceso rápido configurables (F6/F7/F8/F9)
- 🔄 Carga automáticamente el último perfil usado

## Requisitos
- Windows 10/11
- Python 3.10+
- Librerías: `customtkinter pynput pyautogui pillow`

## Instalación
```bash
pip install customtkinter pynput pyautogui pillow
python main.py
```

## Uso
1. Abre Evomon antes de entrar al juego
2. Escribe el nombre del monstruo en **Nombre**
3. Configura el tiempo de respawn
4. Presiona **Grabar** y realiza las acciones en el juego
5. Presiona **Parar** grabación
6. Presiona **Guardar perfil**
7. Presiona **Iniciar** — Evomon hace todo solo

## Teclas por defecto
| Tecla | Acción |
|-------|--------|
| F6 | Iniciar |
| F7 | Detener |
| F8 | Grabar |
| F9 | Parar grabación |

> Las teclas son configurables desde la app.

## Estructura
```
macroMon/
├── main.py
├── ui/
│   └── ventana.py
├── core/
│   ├── grabador.py
│   ├── reproductor.py
│   ├── timer.py
│   └── gestor_perfiles.py
├── data/
│   └── perfiles/
└── assets/
```
