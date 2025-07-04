import streamlit as st
import json
import os
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

from main import speech_to_text, analyze_emotion, generate_image, save_to_history, translate_text

HISTORY_FILE = "history.json"

st.set_page_config(page_title="Synthétiseur de rêves", layout="wide")
st.title("🌙 Synthétiseur de rêves")

# --- Init session state ---
if "audio_frames" not in st.session_state:
    st.session_state["audio_frames"] = []

# --- Classe pour enregistrer l'audio ---
class AudioProcessor:
    def recv(self, frame):
        st.session_state["audio_frames"].append(frame)
        return frame

def save_audio(frames):
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output = av.open(tmp_wav.name, mode='w', format='wav')
    stream = output.add_stream('pcm_s16le', rate=frames[0].sample_rate, layout='mono')
    for frame in frames:
        for packet in stream.encode(frame):
            output.mux(packet)
    for packet in stream.encode(None):
        output.mux(packet)
    output.close()
    return tmp_wav.name

# --- Choix mode d'entrée ---
st.header("1. Enregistrez votre rêve ou téléversez un fichier audio")

mode = st.radio("Choisissez le mode d'entrée audio :", ("Enregistrer", "Téléverser"))
audio_path = None
texte = ""

if mode == "Enregistrer":
    st.session_state["audio_frames"] = []
    ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )
    st.write(f"🎙️ Frames audio capturées : {len(st.session_state['audio_frames'])}")
    if st.button("Arrêter et sauvegarder l'enregistrement"):
        if st.session_state["audio_frames"]:
            audio_path = save_audio(st.session_state["audio_frames"])
            st.success(f"✅ Audio sauvegardé : {audio_path}")
        else:
            st.warning("⚠️ Aucun audio enregistré.")

elif mode == "Téléverser":
    uploaded_file = st.file_uploader("Choisissez un fichier audio", type=["mp3", "mp4", "wav", "m4a"])
    if uploaded_file is not None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        tmp_file.write(uploaded_file.read())
        tmp_file.close()
        audio_path = tmp_file.name
        st.success(f"✅ Fichier téléversé : {audio_path}")

# --- Traitement si audio présent ---
if audio_path:
    st.header("2. Transcription")
    with st.spinner("⏳ Transcription en cours..."):
        texte = speech_to_text(audio_path)
    st.text_area("📝 Texte extrait du rêve :", texte, height=200)

    st.header("2 bis. Traduction")
    languages = {
        "Anglais": "anglais",
        "Espagnol": "espagnol",
        "Allemand": "allemand",
        "Italien": "italien",
        "Portugais": "portugais",
        "Arabe": "arabe",
        "Japonais": "japonais",
        "Chinois (simplifié)": "chinois simplifié",
        "Russe": "russe",
        "Hindi": "hindi"
    }

    selected_language = st.selectbox("🌍 Traduire en :", list(languages.keys()))
    if st.button("Traduire"):
        with st.spinner(f"Traduction en {selected_language}..."):
            translated_text = translate_text(texte, languages[selected_language])
        st.text_area(f"📘 Texte traduit en {selected_language} :", translated_text, height=200)

    st.header("3. Analyse des émotions")
    with st.spinner("🔍 Analyse en cours..."):
        emotions = analyze_emotion(texte)
    st.json(emotions)

    st.subheader("📊 Diagramme des émotions")
    fig, ax = plt.subplots()
    ax.pie(emotions.values(), labels=emotions.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    st.header("4. Image générée à partir du rêve")
    with st.spinner("🎨 Génération de l’image..."):
        image_path = generate_image(texte)
    st.image(image_path, caption="🖼️ Rêve illustré")

    st.header("5. Sauvegarde")
    if st.button("💾 Sauvegarder ce rêve"):
        save_to_history(texte, emotions, image_path)
        st.success("✅ Rêve sauvegardé dans l’historique")

# --- Historique ---
if os.path.exists(HISTORY_FILE):
    st.header("📜 Historique des rêves")
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    for item in reversed(history):
        with st.expander(f"🕰️ Rêve du {datetime.fromisoformat(item['timestamp']).strftime('%d/%m/%Y %H:%M')}"):
            st.text_area("Texte", item['text'], height=100, key=item['timestamp'])
            st.image(item['image_path'], width=300)
            st.json(item['emotions'])



# import streamlit as st
# import av
# import numpy as np
# import tempfile
# import os
# import json
# from datetime import datetime
# import matplotlib.pyplot as plt
# from streamlit_webrtc import webrtc_streamer, WebRtcMode

# # Configuration
# HISTORY_FILE = "history.json"
# st.set_page_config(page_title="Synthétiseur de rêves", layout="wide")
# st.title("🎙️ Synthétiseur de rêves")

# # Initialisation session state
# if 'audio_frames' not in st.session_state:
#     st.session_state.audio_frames = []
# if 'recording' not in st.session_state:
#     st.session_state.recording = False
# if 'webrtc_ctx' not in st.session_state:
#     st.session_state.webrtc_ctx = None

# class AudioProcessor:
#     def recv(self, frame):
#         if st.session_state.recording:
#             frame_np = frame.to_ndarray(format="s16")
#             st.session_state.audio_frames.append(frame_np)
#         return frame

# def save_audio(frames, sample_rate=44100):
#     """Sauvegarde les frames audio en fichier WAV"""
#     tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    
#     container = av.open(tmp_wav.name, mode='w')
#     stream = container.add_stream('pcm_s16le', rate=sample_rate)
#     stream.layout = 'mono'

#     for frame_np in frames:
#         frame = av.AudioFrame.from_ndarray(
#             frame_np.reshape(1, -1), 
#             format='s16', 
#             layout='mono'
#         )
#         frame.rate = sample_rate
#         for packet in stream.encode(frame):
#             container.mux(packet)

#     # Finaliser l'encodage
#     for packet in stream.encode(None):
#         container.mux(packet)
    
#     container.close()
#     return tmp_wav.name

# # Interface
# st.header("1. Enregistrement audio")

# mode = st.radio("Mode d'entrée :", ("Microphone", "Fichier"))

# if mode == "Microphone":
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("🔴 Démarrer l'enregistrement"):
#             st.session_state.recording = True
#             st.session_state.audio_frames = []
#             st.success("Enregistrement démarré - parlez maintenant")

#     with col2:
#         if st.button("⏹ Arrêter et sauvegarder"):
#             st.session_state.recording = False
#             if len(st.session_state.audio_frames) > 0:
#                 audio_path = save_audio(st.session_state.audio_frames)
#                 st.session_state.audio_path = audio_path
#                 st.success(f"Audio sauvegardé ({len(st.session_state.audio_frames)} frames)")
#                 st.session_state.audio_frames = []  # Réinitialiser
#             else:
#                 st.warning("Aucun audio capturé")

#     # WebRTC doit être après les boutons pour fonctionner correctement
#     st.session_state.webrtc_ctx = webrtc_streamer(
#         key="audio-recorder",
#         mode=WebRtcMode.SENDRECV,
#         audio_processor_factory=AudioProcessor,
#         media_stream_constraints={"audio": True, "video": False},
#         async_processing=True,
#     )

# elif mode == "Fichier":
#     uploaded_file = st.file_uploader("Téléversez un fichier audio", type=["mp3", "mp4", "wav", "m4a"])
#     if uploaded_file:
#         ext = os.path.splitext(uploaded_file.name)[1]
#         with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
#             tmp_file.write(uploaded_file.read())
#             st.session_state.audio_path = tmp_file.name
#         st.success("Fichier audio prêt pour analyse")

# # Fonctions simulées (à remplacer par vos implémentations)
# def speech_to_text(audio_path):
#     return "Ceci est une transcription simulée. Remplacez par Whisper/API similaire."

# def analyze_emotion(text):
#     return {"joie": 40, "peur": 20, "tristesse": 15, "colère": 10, "surprise": 15}

# def generate_image(text):
#     return "https://via.placeholder.com/600x400?text=Image+simulée"

# def save_to_history(text, emotions, image_path):
#     history = []
#     if os.path.exists(HISTORY_FILE):
#         with open(HISTORY_FILE, "r") as f:
#             history = json.load(f)
    
#     history.append({
#         "timestamp": datetime.now().isoformat(),
#         "text": text,
#         "emotions": emotions,
#         "image_path": image_path
#     })
    
#     with open(HISTORY_FILE, "w") as f:
#         json.dump(history, f, indent=2)

# # Suite du traitement si audio disponible
# if 'audio_path' in st.session_state and st.session_state.audio_path:
#     st.header("2. Analyse du rêve")
    
#     with st.spinner("Transcription en cours..."):
#         texte = speech_to_text(st.session_state.audio_path)
#     st.text_area("Transcription", texte, height=150)

#     with st.spinner("Analyse des émotions..."):
#         emotions = analyze_emotion(texte)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Répartition émotionnelle")
#         fig, ax = plt.subplots()
#         ax.pie(emotions.values(), labels=emotions.keys(), autopct="%1.1f%%")
#         st.pyplot(fig)
#     with col2:
#         st.subheader("Détails")
#         st.json(emotions)

#     st.subheader("Illustration du rêve")
#     img_path = generate_image(texte)
#     st.image(img_path, width=400)

#     if st.button("💾 Sauvegarder dans l'historique"):
#         save_to_history(texte, emotions, img_path)
#         st.success("Rêve sauvegardé !")

# # Historique
# if os.path.exists(HISTORY_FILE):
#     st.header("Historique des rêves")
#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
    
#     for item in reversed(history):
#         with st.expander(f"Rêve du {datetime.fromisoformat(item['timestamp']).strftime('%d/%m/%Y %H:%M')}"):
#             st.text_area("Texte", item['text'], height=100, key=item['timestamp'])
#             st.image(item['image_path'], width=300)
#             st.json(item['emotions'])


