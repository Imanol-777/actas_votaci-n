import tkinter as tk

from config import JACK_IMG_H, JACK_IMG_H, JACK_IMG_W

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False


def make_photo(path):
    """Devuelve un PhotoImage escalado para caber dentro de la carta."""
    if HAS_PIL:
        im = Image.open(path).convert("RGBA")
        im.thumbnail((JACK_IMG_W, JACK_IMG_H))
        return ImageTk.PhotoImage(im)

    img = tk.PhotoImage(file=path)
    fw = max(1, -(-img.width() // JACK_IMG_W))
    fh = max(1, -(-img.height() // JACK_IMG_H))
    f = max(fw, fh)
    if f > 1:
        img = img.subsample(f, f)
    return img
