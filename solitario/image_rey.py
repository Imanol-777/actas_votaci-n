import tkinter as tk

from config import KING_IMG_W, KING_IMG_H

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False


def make_photo(path):
    """Devuelve un PhotoImage escalado para caber dentro de la carta."""
    if HAS_PIL:
        im = Image.open(path).convert("RGBA")
        im.thumbnail((KING_IMG_W, KING_IMG_H))
        return ImageTk.PhotoImage(im)

    img = tk.PhotoImage(file=path)
    fw = max(1, -(-img.width() // KING_IMG_W))
    fh = max(1, -(-img.height() // KING_IMG_H))
    f = max(fw, fh)
    if f > 1:
        img = img.subsample(f, f)
    return img
