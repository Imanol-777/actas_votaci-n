"""
corregir_fotos.py
=================
Corrige la inclinación de fotos con tablas usando detección automática de ángulo.

Uso:
    # Una sola foto:
    python corregir_fotos.py foto.jpg

    # Carpeta completa:
    python corregir_fotos.py carpeta/

    # Especificar carpeta de salida:
    python corregir_fotos.py carpeta/ --salida carpeta_corregida/

Dependencias:
    pip install opencv-python numpy Pillow
"""

import cv2
import numpy as np
from pathlib import Path
import argparse
import sys


# ─── Extensiones de imagen soportadas ───────────────────────────────────────
EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def detectar_angulo(imagen_gris: np.ndarray) -> float:
    """
    Detecta el ángulo de inclinación de una imagen usando dos métodos:
    1. Transformada de Hough (líneas rectas → ideal para tablas)
    2. Mínimo rectángulo delimitador del texto (fallback)
    Retorna el ángulo en grados.
    """
    alto, ancho = imagen_gris.shape

    # ── Método 1: Hough Lines (funciona muy bien con tablas) ──────────────
    bordes = cv2.Canny(imagen_gris, 50, 150, apertureSize=3)
    lineas = cv2.HoughLinesP(
        bordes,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=ancho // 5,
        maxLineGap=20,
    )

    angulos_hough = []
    if lineas is not None:
        for linea in lineas:
            x1, y1, x2, y2 = linea[0]
            if x2 != x1:
                angulo = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                # Solo líneas casi horizontales o casi verticales
                if abs(angulo) < 45:
                    angulos_hough.append(angulo)
                elif abs(abs(angulo) - 90) < 45:
                    angulos_hough.append(angulo - np.sign(angulo) * 90)

    if len(angulos_hough) >= 5:
        # Mediana para ignorar outliers
        angulo_final = float(np.median(angulos_hough))
        # Si el ángulo es mínimo, no vale la pena corregir
        if abs(angulo_final) < 0.3:
            return 0.0
        return angulo_final

    # ── Método 2: Contornos + MinAreaRect (fallback) ──────────────────────
    _, binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contornos:
        return 0.0

    # Usar el contorno más grande
    contorno_grande = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(contorno_grande) < (alto * ancho * 0.01):
        return 0.0

    rect = cv2.minAreaRect(contorno_grande)
    angulo = rect[-1]

    # Normalizar ángulo al rango (-45, 45)
    if angulo < -45:
        angulo += 90
    elif angulo > 45:
        angulo -= 90

    return float(angulo)


def rotar_imagen(imagen: np.ndarray, angulo: float) -> np.ndarray:
    """
    Rota la imagen el ángulo indicado sin recortar bordes.
    Rellena el fondo con blanco.
    """
    alto, ancho = imagen.shape[:2]
    centro = (ancho // 2, alto // 2)

    M = cv2.getRotationMatrix2D(centro, angulo, 1.0)

    # Calcular nuevo tamaño para no recortar
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    nuevo_ancho = int(alto * sin + ancho * cos)
    nuevo_alto = int(alto * cos + ancho * sin)

    # Ajustar matriz de rotación al nuevo centro
    M[0, 2] += (nuevo_ancho - ancho) / 2
    M[1, 2] += (nuevo_alto - alto) / 2

    rotada = cv2.warpAffine(
        imagen,
        M,
        (nuevo_ancho, nuevo_alto),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    return rotada


def corregir_foto(ruta_entrada: Path, ruta_salida: Path) -> dict:
    """
    Carga una foto, detecta su inclinación y la corrige.
    Retorna un dict con el resultado.
    """
    imagen = cv2.imread(str(ruta_entrada))
    if imagen is None:
        return {"archivo": ruta_entrada.name, "ok": False, "error": "No se pudo leer el archivo"}

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    angulo = detectar_angulo(gris)

    if abs(angulo) < 0.3:
        # Sin inclinación significativa — copiar tal cual
        cv2.imwrite(str(ruta_salida), imagen)
        return {"archivo": ruta_entrada.name, "ok": True, "angulo": 0.0, "nota": "Sin corrección necesaria"}

    corregida = rotar_imagen(imagen, angulo)
    cv2.imwrite(str(ruta_salida), corregida)

    return {"archivo": ruta_entrada.name, "ok": True, "angulo": round(angulo, 2)}


def procesar(entrada: Path, salida_dir: Path):
    """Procesa una imagen o una carpeta completa."""

    # ── Determinar lista de archivos a procesar ───────────────────────────
    if entrada.is_file():
        if entrada.suffix.lower() not in EXTENSIONES:
            print(f"❌  '{entrada.name}' no es una imagen soportada.")
            sys.exit(1)
        archivos = [entrada]
        salida_dir = salida_dir or entrada.parent / "corregidas"
    elif entrada.is_dir():
        archivos = sorted(
            f for f in entrada.iterdir() if f.suffix.lower() in EXTENSIONES
        )
        if not archivos:
            print(f"❌  No se encontraron imágenes en '{entrada}'.")
            sys.exit(1)
        salida_dir = salida_dir or entrada / "corregidas"
    else:
        print(f"❌  '{entrada}' no existe.")
        sys.exit(1)

    salida_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁  Guardando resultados en: {salida_dir}\n")
    print(f"{'Archivo':<35} {'Ángulo':>8}  {'Estado'}")
    print("─" * 60)

    ok = err = 0
    for archivo in archivos:
        ruta_salida = salida_dir / archivo.name
        resultado = corregir_foto(archivo, ruta_salida)

        if resultado["ok"]:
            nota = resultado.get("nota", f"{resultado['angulo']:+.2f}°")
            print(f"  ✅  {resultado['archivo']:<30} {nota:>10}")
            ok += 1
        else:
            print(f"  ❌  {resultado['archivo']:<30}  ERROR: {resultado['error']}")
            err += 1

    print("─" * 60)
    print(f"\n  {ok} imagen(s) procesada(s) correctamente", end="")
    if err:
        print(f"  |  {err} con error(es)", end="")
    print("\n")


# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Corrige la inclinación de fotos con tablas.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python corregir_fotos.py foto.jpg
  python corregir_fotos.py mis_fotos/
  python corregir_fotos.py mis_fotos/ --salida fotos_listas/
        """,
    )
    parser.add_argument("entrada", help="Foto o carpeta de fotos a corregir")
    parser.add_argument(
        "--salida", "-o", default=None, help="Carpeta donde guardar las fotos corregidas"
    )
    args = parser.parse_args()

    entrada = Path(args.entrada)
    salida = Path(args.salida) if args.salida else None

    procesar(entrada, salida)


if __name__ == "__main__":
    main()
