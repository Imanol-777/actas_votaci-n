import os
import base64
import json
from openai import AzureOpenAI

# =========================
# CONFIG
# =========================
# Credenciales y configuración de Azure OpenAI
endpoint = "https://jidiazv-2085-resource.cognitiveservices.azure.com/"
deployment = "gpt-5.4-nano"
subscription_key = "3ywyZumel77d7UVVjlGQ99NF1Qe2He6G3tzRgP1eahyaOTcZSoeAJQQJ99CCACHYHv6XJ3w3AAAAACOG3U6V"
api_version = "2024-12-01-preview"

# Carpeta donde están las fotos de las actas
CARPETA_IMAGENES = "corregidas"
# Carpeta donde se guardarán los JSON con los resultados
CARPETA_SALIDA = "json_resultados"

os.makedirs(CARPETA_SALIDA, exist_ok=True)

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


# =========================
# FUNCIONES
# =========================
def imagen_a_base64(ruta_imagen):
    # Carga la imagen y la convierte a base64 para enviarla a la IA
    with open(ruta_imagen, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extraer_contenido_respuesta(response):
    # Extrae el texto de la respuesta de forma segura
    try:
        mensaje = response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"No se pudo acceder a response.choices[0].message.content: {e}")

    if mensaje is None:
        raise ValueError("La respuesta del modelo vino vacía (content=None).")

    if isinstance(mensaje, str):
        return mensaje.strip()

    elif isinstance(mensaje, list):
        partes_texto = []
        for bloque in mensaje:
            if isinstance(bloque, dict):
                if bloque.get("type") == "text":
                    partes_texto.append(bloque.get("text", ""))
            elif hasattr(bloque, "text"):
                partes_texto.append(bloque.text)

        contenido = "\n".join(partes_texto).strip()
        if not contenido:
            raise ValueError("La respuesta vino como lista, pero no contenía texto útil.")
        return contenido

    else:
        raise ValueError(f"Formato inesperado en message.content: {type(mensaje)}")


def limpiar_json_markdown(texto):
    # Elimina los bloques ```json ``` que a veces agrega la IA
    return texto.replace("```json", "").replace("```", "").strip()


def procesar_imagen(ruta_imagen):
    # Procesa una imagen: la manda a Azure, extrae los votos y guarda el resultado como .json
    nombre_archivo = os.path.basename(ruta_imagen)
    nombre_base, _ = os.path.splitext(nombre_archivo)

    print(f"\nProcesando: {nombre_archivo}")

    try:
        imagen_base64 = imagen_a_base64(ruta_imagen)

        response = client.chat.completions.create(
            model=deployment,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en extracción de datos de actas electorales. "
                        "Devuelve SOLO JSON válido. "
                        "No agregues explicaciones, encabezados, ni texto adicional."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Esta imagen es una tabla de resultados electorales mexicana. "
                                "Cada fila tiene uno o varios logos de partidos a la izquierda y votos a la derecha.\n\n"
                                "Los partidos posibles son: PAN, PRI, PRD, PVEM, PT, MC, MORENA, ALIANZA, y combinaciones de estos.\n"
                                "Los logos de cada partido tienen estos colores:\n"
                                "- PAN: azul\n"
                                "- PRI: rojo y verde\n"
                                "- PRD: amarillo\n"
                                "- PVEM: verde\n"
                                "- PT: rojo\n"
                                "- MORENA: guinda/vino\n"
                                "- MC: naranja\n\n"
                                "Si una fila tiene varios logos juntos, es una coalición, escríbela como 'PAN-PRI' o 'PT-MORENA' etc.\n"
                                "Los números están escritos dígito por dígito, '0 8 7' significa 87.\n\n"
                                "Devuelve SOLO este JSON:\n"
                                "{\n"
                                '  "acta": "nombre_del_archivo",\n'
                                '  "resultados": [{"partido": "nombre", "votos": numero}],\n'
                                '  "votos_nulos": 0,\n'
                                '  "total": 0\n'
                                "}"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{imagen_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        contenido = extraer_contenido_respuesta(response)
        contenido_limpio = limpiar_json_markdown(contenido)

        try:
            data = json.loads(contenido_limpio)

            if "acta" not in data or not data["acta"]:
                data["acta"] = nombre_base

            with open(
                os.path.join(CARPETA_SALIDA, f"{nombre_base}.json"),
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ JSON guardado: {nombre_base}.json")

        except Exception as e_json:
            print(f"❌ Error parseando JSON en {nombre_archivo}: {e_json}")
            with open(
                os.path.join(CARPETA_SALIDA, f"{nombre_base}_error_parseo.txt"),
                "w",
                encoding="utf-8"
            ) as f:
                f.write(contenido_limpio)

    except Exception as e:
        print(f"❌ Error procesando {nombre_archivo}: {e}")
        with open(
            os.path.join(CARPETA_SALIDA, f"{nombre_base}_error_general.txt"),
            "w",
            encoding="utf-8"
        ) as f:
            f.write(str(e))


# =========================
# MAIN
# =========================
def main():
    # Punto de entrada: busca todas las imágenes en actas_resultados y las procesa
    if not os.path.exists(CARPETA_IMAGENES):
        print(f"❌ La carpeta '{CARPETA_IMAGENES}' no existe.")
        return

    archivos = [
        f for f in os.listdir(CARPETA_IMAGENES)
        if f.lower().endswith(EXTENSIONES_VALIDAS)
    ]

    if not archivos:
        print("⚠ No se encontraron imágenes para procesar.")
        return

    print(f"Se encontraron {len(archivos)} imagen(es) listas para procesar.")

    for archivo in archivos:
        ruta_imagen = os.path.join(CARPETA_IMAGENES, archivo)
        procesar_imagen(ruta_imagen)

    print("\n🎉 Proceso terminado.")


if __name__ == "__main__":
    main()
