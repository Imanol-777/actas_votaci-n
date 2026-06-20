import os
import json
import glob
import shutil

# Carpeta donde se guardan las imágenes
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes_guardadas")
INDEX = os.path.join(BASE, "index.json")

TIPOS = ("rey", "as", "reina", "jota")


def _leer_index():
    try:
        with open(INDEX, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        data = {}
    return {t: dict(data.get(t, {})) for t in TIPOS}


def _escribir_index(idx):
    os.makedirs(BASE, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=2)


def guardar(kind, suit, src_path):
    """Copia la imagen a la carpeta del juego y la registra. Devuelve la ruta."""
    os.makedirs(BASE, exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower() or ".png"
    nombre = "%s_%s%s" % (kind, suit, ext)
    dst = os.path.join(BASE, nombre)

    # borrar versiones previas del mismo hueco con otra extensión
    for viejo in glob.glob(os.path.join(BASE, "%s_%s.*" % (kind, suit))):
        if os.path.abspath(viejo) != os.path.abspath(dst):
            try:
                os.remove(viejo)
            except OSError:
                pass

    if os.path.abspath(src_path) != os.path.abspath(dst):
        shutil.copyfile(src_path, dst)

    idx = _leer_index()
    idx.setdefault(kind, {})[suit] = nombre
    _escribir_index(idx)
    return dst


def borrar_tipo(kind):
    """Elimina las imágenes guardadas de un tipo (p. ej. todos los reyes)."""
    idx = _leer_index()
    for nombre in idx.get(kind, {}).values():
        try:
            os.remove(os.path.join(BASE, nombre))
        except OSError:
            pass
    idx[kind] = {}
    _escribir_index(idx)


def cargar_todo():
    """Devuelve {kind: {suit: ruta_absoluta}} de las imágenes que existen."""
    idx = _leer_index()
    salida = {}
    for kind, palos in idx.items():
        for suit, nombre in palos.items():
            ruta = os.path.join(BASE, nombre)
            if os.path.exists(ruta):
                salida.setdefault(kind, {})[suit] = ruta
    return salida
