import tkinter as tk

from config import QUEEN_IMG_H, QUEEN_IMG_H, QUEEN_IMG_W

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False


def make_photo(path):
    """Devuelve un PhotoImage escalado para caber dentro de la carta."""
    if HAS_PIL:
        im = Image.open(path).convert("RGBA")
        im.thumbnail((QUEEN_IMG_W, QUEEN_IMG_H))
        return ImageTk.PhotoImage(im)

    img = tk.PhotoImage(file=path)
    fw = max(1, -(-img.width() // QUEEN_IMG_W))
    fh = max(1, -(-img.height() // QUEEN_IMG_H))
    f = max(fw, fh)
    if f > 1:
        img = img.subsample(f, f)
    return img
