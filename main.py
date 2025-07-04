# import os
# import json
# import math
# import re
# import requests
# from typing import Dict
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY")

# client = Groq(api_key=GROQ_API_KEY)


# def read_file(file_path: str) -> str:
#     with open(file_path, "r", encoding="utf-8") as file:
#         return file.read()


# def softmax(predictions: Dict[str, float]) -> Dict[str, float]:
#     exp_values = [math.exp(v * 10) for v in predictions.values()]
#     total = sum(exp_values)
#     return {k: math.exp(v * 10) / total for k, v in predictions.items()}


# def speech_to_text(audio_path: str, language: str = "fr") -> str:
#     with open(audio_path, "rb") as file:
#         transcription = client.audio.transcriptions.create(
#             file=file,
#             model="whisper-large-v3",
#             prompt="Transcris le rêve le plus fidèlement possible.",
#             response_format="verbose_json",
#             timestamp_granularities=["segment"],
#             language=language,
#             temperature=0.0
#         )
#     return transcription.text


# def analyze_emotion(text: str, context_file: str = "context_analysis.txt") -> Dict[str, float]:
#     context = read_file(context_file)

#     response = client.chat.completions.create(
#         model="mistral-saba-24b",
#         messages=[
#             {"role": "system", "content": context},
#             {"role": "user", "content": text}
#         ],
#         temperature=0.0
#     )

#     content = response.choices[0].message.content
#     match = re.search(r"\{.*\}", content, re.DOTALL)
#     if match:
#         json_str = match.group(0)
#         try:
#             emotions = json.loads(json_str)
#             return softmax(emotions)
#         except json.JSONDecodeError:
#             print("❌ Erreur de décodage JSON.")
#             print(content)
#             return {}
#     else:
#         print("❌ Pas de JSON détecté dans la réponse :")
#         print(content)
#         return {}


# def generate_image(prompt: str, output_path: str = "dream_image.png") -> str:
#     url = "https://clipdrop-api.co/text-to-image/v1"
#     headers = {"x-api-key": CLIPDROP_API_KEY}
#     data = {
#         "prompt": prompt
#     }

#     response = requests.post(url, headers=headers, json=data)

#     if response.status_code == 200:
#         with open(output_path, "wb") as f:
#             f.write(response.content)
#         return output_path
#     else:
#         raise Exception(f"Erreur Clipdrop : {response.status_code} - {response.text}")


# if __name__ == "__main__":
#     audio_path = "../audio.mp4"

#     print("🎙 Transcription...")
#     text = speech_to_text(audio_path)
#     print(f"\n📝 Texte extrait :\n{text}\n")

#     print("🔍 Analyse des émotions...")
#     emotions = analyze_emotion(text)
#     print(f"\n📊 Émotions détectées :\n{emotions}\n")

#     print("🖼 Génération de l’image...")
#     image_path = generate_image(text)
#     print(f"\n📁 Image sauvegardée ici : {image_path}")


import os
import json
import math
import re
import requests
from typing import Dict
from dotenv import load_dotenv
from datetime import datetime
from groq import Groq

# 🔐 Chargement des clés API
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY")
HISTORY_FILE = "history.json"

client = Groq(api_key=GROQ_API_KEY)

# 📂 Fonctions utilitaires
def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def softmax(predictions: Dict[str, float]) -> Dict[str, float]:
    exp_values = [math.exp(v * 10) for v in predictions.values()]
    total = sum(exp_values)
    return {k: math.exp(v * 10) / total for k, v in predictions.items()}

def speech_to_text(audio_path: str, language: str = "fr") -> str:
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            prompt="Transcris le rêve le plus fidèlement possible.",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            language=language,
            temperature=0.0
        )
    return transcription.text

def analyze_emotion(text: str, context_file: str = "context_analysis.txt") -> Dict[str, float]:
    context = read_file(context_file)
    response = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": text}
        ],
        temperature=0.0
    )
    content = response.choices[0].message.content
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            emotions = json.loads(json_str)
            return softmax(emotions)
        except json.JSONDecodeError:
            print("❌ Erreur de décodage JSON.")
            print(content)
            return {}
    else:
        print("❌ Pas de JSON détecté dans la réponse :")
        print(content)
        return {}

def generate_image(prompt: str, output_path: str = "dream_image.png") -> str:
    url = "https://clipdrop-api.co/text-to-image/v1"
    headers = {"x-api-key": CLIPDROP_API_KEY}
    data = {
        "prompt": prompt
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"Erreur Clipdrop : {response.status_code} - {response.text}")

def translate_text(text: str, target_language: str) -> str:
    prompt = f"Traduis ce texte en {target_language} :\n\n{text}"
    response = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()



def save_to_history(text: str, emotions: Dict[str, float], image_path: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "emotions": emotions,
        "image_path": image_path
    }
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# 🚀 Programme principal
if __name__ == "__main__":
    audio_path = "../audio2.mp4"

    print("🎙 Transcription...")
    text = speech_to_text(audio_path)
    print(f"\n📝 Texte extrait :\n{text}\n")

    print("🔍 Analyse des émotions...")
    emotions = analyze_emotion(text)
    print(f"\n📊 Émotions détectées :\n{emotions}\n")

    print("🖼 Génération de l’image...")
    image_path = generate_image(text)
    print(f"\n📁 Image sauvegardée ici : {image_path}")

    print("💾 Sauvegarde de l’historique...")
    save_to_history(text, emotions, image_path)
    print("✅ Rêve sauvegardé dans 'history.json'")
