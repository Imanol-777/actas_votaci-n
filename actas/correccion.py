"""
corregir_fotos.py
=================
Corrige la inclinación de fotos con tablas usando detección automática de ángulo.

Uso:
    python corregir_fotos.py foto.jpg
    python corregir_fotos.py carpeta/
    python corregir_fotos.py carpeta/ --salida carpeta_corregida/

Dependencias:
    pip install opencv-python numpy Pillow
"""

import cv2
import numpy as np
from pathlib import Path
import argparse
import sys


EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def detectar_angulo(imagen_gris: np.ndarray) -> float:
    alto, ancho = imagen_gris.shape

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
                if abs(angulo) < 45:
                    angulos_hough.append(angulo)
                elif abs(abs(angulo) - 90) < 45:
                    angulos_hough.append(angulo - np.sign(angulo) * 90)

    if len(angulos_hough) >= 5:
        angulo_final = float(np.median(angulos_hough))
        if abs(angulo_final) < 0.3:
            return 0.0
        return angulo_final

    _, binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contornos:
        return 0.0

    contorno_grande = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(contorno_grande) < (alto * ancho * 0.01):
        return 0.0

    rect = cv2.minAreaRect(contorno_grande)
    angulo = rect[-1]

    if angulo < -45:
        angulo += 90
    elif angulo > 45:
        angulo -= 90

    return float(angulo)


def rotar_imagen(imagen: np.ndarray, angulo: float) -> np.ndarray:
    alto, ancho = imagen.shape[:2]
    centro = (ancho // 2, alto // 2)

    M = cv2.getRotationMatrix2D(centro, angulo, 1.0)

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    nuevo_ancho = int(alto * sin + ancho * cos)
    nuevo_alto = int(alto * cos + ancho * sin)

    M[0, 2] += (nuevo_ancho - ancho) / 2
    M[1, 2] += (nuevo_alto - alto) / 2

    return cv2.warpAffine(
        imagen,
        M,
        (nuevo_ancho, nuevo_alto),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def corregir_foto(actas_resultados: Path, ruta_salida: Path) -> dict:
    imagen = cv2.imread(str(actas_resultados))

    if imagen is None:
        return {
            "archivo": actas_resultados.name,
            "ok": False,
            "error": "No se pudo leer el archivo"
        }

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    angulo = detectar_angulo(gris)

    # 👉 Generar nombre con sufijo "_corregida"
    nombre_salida = ruta_salida.with_stem(actas_resultados.stem + "_corregida")

    if abs(angulo) < 0.3:
        cv2.imwrite(str(nombre_salida), imagen)
        return {
            "archivo": actas_resultados.name,
            "ok": True,
            "angulo": 0.0,
            "nota": "Sin corrección necesaria"
        }

    corregida = rotar_imagen(imagen, angulo)
    cv2.imwrite(str(nombre_salida), corregida)

    return {
        "archivo": actas_resultados.name,
        "ok": True,
        "angulo": round(angulo, 2)
    }


def procesar(entrada: Path, salida_dir: Path):
    if entrada.is_file():
        if entrada.suffix.lower() not in EXTENSIONES:
            print(f"❌ '{entrada.name}' no es una imagen soportada.")
            sys.exit(1)
        archivos = [entrada]
        salida_dir = salida_dir or entrada.parent / "corregidas"

    elif entrada.is_dir():
        archivos = sorted(
            f for f in entrada.iterdir() if f.suffix.lower() in EXTENSIONES
        )
        if not archivos:
            print(f"❌ No se encontraron imágenes en '{entrada}'.")
            sys.exit(1)
        salida_dir = salida_dir or entrada / "corregidas"

    else:
        print(f"❌ '{entrada}' no existe.")
        sys.exit(1)

    salida_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Guardando resultados en: {salida_dir}\n")
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
            print(f"  ❌  {resultado['archivo']:<30} ERROR: {resultado['error']}")
            err += 1

    print("─" * 60)
    print(f"\n  {ok} imagen(es) procesada(s) correctamente", end="")
    if err:
        print(f" | {err} con error(es)", end="")
    print("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Corrige la inclinación de fotos con tablas."
    )
    parser.add_argument("entrada", help="Foto o carpeta de fotos")
    parser.add_argument("--salida", "-o", help="Carpeta de salida")

    args = parser.parse_args()

    entrada = Path(args.entrada)
    salida = Path(args.salida) if args.salida else None

    procesar(entrada, salida)


if __name__ == "__main__":
    main()