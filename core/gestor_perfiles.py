import json
import os

CARPETA_PERFILES = os.path.join(os.path.dirname(__file__), "..", "data", "perfiles")
_RUTA_CONFIG     = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")

def _ruta(nombre):
    return os.path.join(CARPETA_PERFILES, f"{nombre}.json")

def guardar_perfil(nombre, minutos, segundos, acciones):
    os.makedirs(CARPETA_PERFILES, exist_ok=True)
    datos = {
        "nombre": nombre,
        "respawn_minutos": minutos,
        "respawn_segundos": segundos,
        "acciones": acciones
    }
    with open(_ruta(nombre), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    guardar_ultimo_perfil(nombre)

def cargar_perfil(nombre):
    ruta = _ruta(nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def listar_perfiles():
    os.makedirs(CARPETA_PERFILES, exist_ok=True)
    archivos = [f.replace(".json", "") for f in os.listdir(CARPETA_PERFILES) if f.endswith(".json")]
    return sorted(archivos)

def eliminar_perfil(nombre):
    ruta = _ruta(nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    return False

def guardar_ultimo_perfil(nombre):
    os.makedirs(os.path.dirname(_RUTA_CONFIG), exist_ok=True)
    with open(_RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"ultimo_perfil": nombre}, f)

def cargar_ultimo_perfil():
    if not os.path.exists(_RUTA_CONFIG):
        return None
    with open(_RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f).get("ultimo_perfil")
