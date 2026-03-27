import os
from openai import AzureOpenAI
import base64
#pip install openai
endpoint = "https://jidiazv-2085-resource.cognitiveservices.azure.com/"
model_name = "gpt-5.4-nano"
deployment = "gpt-5.4-nano"

subscription_key = "3ywyZumel77d7UVVjlGQ99NF1Qe2He6G3tzRgP1eahyaOTcZSoeAJQQJ99CCACHYHv6XJ3w3AAAAACOG3U6V"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

with open("AYU_5134_001_1.jpg", "rb") as f:
    imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Eres un experto en extracción de datos. Devuelve SOLO JSON válido."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extrae la tabla de la imagen y conviértela en un JSON con el nombre del partido y total de votos"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imagen_base64}"
                    }
                }
            ]
        }
    ],
    temperature=0,
    model=deployment
)

print(response.choices[0].message.content)