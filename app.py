import streamlit as st
from PIL import Image
from google import genai
from google.genai import types as genai_types
import os
import io
import json
import zipfile
import tempfile
import uuid

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .stTabs [data-baseweb="tab"] {
            font-size: 18px;
            height: 60px;
            padding: 10px 30px;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f5f5f5;
            color: black;
        }
        .stTextArea, .stTextInput, .stSelectbox, .stMultiSelect, .stRadio, .stFileUploader, .stButton, .stImage, .stRadio label {
            border: 2px solid #333 !important;
            border-radius: 8px;
            padding: 8px;
        }
        .stTextArea textarea, .stTextInput input, .stSelectbox div, .stMultiSelect div, .stRadio div {
            padding: 4px;
        }
        .element-container:has(.stImage) {
            border: 2px solid #333 !important;
            border-radius: 8px;
            padding: 8px;
        }
        section[data-testid="column"] {
            border-right: 3px solid #ccc;
            padding-right: 20px;
        }
        section[data-testid="column"]:last-of-type {
            border-right: none;
        }
    </style>
""", unsafe_allow_html=True)

import requests


def faq_via_api(question):
    response = requests.post("http://localhost:8000/faq", json={"question": question})
    return response.json()


def analyze_via_api(image_bytes, style, features):
    files = {'file': ('image.png', image_bytes, 'image/png')}
    data = {
        'style': style,
        'features': json.dumps(features)  # ważne: zakoduj listę jako string JSON
    }

    response = requests.post("http://localhost:8000/analyze", files=files, data=data)

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd zapytania: {e}")
        st.text(f"Odpowiedź serwera:\n{response.text}")
        return {"description": "(błąd)", "tags": []}


def generate_faq_answer(question, client, model_id):
    prompt = f"Odpowiedz jak najlepiej na poniższe pytanie FAQ:\n{question}"
    contents = [genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])]
    response = client.models.generate_content(model=model_id, contents=contents)
    return response.text.strip()

if "generated" not in st.session_state:
    st.session_state.generated = False
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "description" not in st.session_state:
    st.session_state.description = ""
if "tags1" not in st.session_state:
    st.session_state.tags1 = ""
if "tags2" not in st.session_state:
    st.session_state.tags2 = ""
if "faq_history" not in st.session_state:
    st.session_state.faq_history = []
if "results" not in st.session_state:
    st.session_state.results = {}


tabs = st.tabs(["TAG", "FAQ"])

with tabs[0]:
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")

    with col1:
        st.subheader("Historia plików")
        uploaded_files = st.file_uploader("Dodaj pliki", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        if uploaded_files:
            selected = st.radio("Wybierz plik", [f.name for f in uploaded_files])
            st.session_state.selected_file = selected
        else:
            st.session_state.selected_file = None

    with col2:
        if uploaded_files and st.session_state.selected_file and st.session_state.generated:
            st.subheader("Opis")
            st.text_area("", st.session_state.description, height=100)

            st.subheader("Tagi")
            col21, col22 = st.columns(2)
            with col21:
                st.text_area("Tagi 1", st.session_state.tags1, height=80)
            with col22:
                st.text_area("Tagi 2", st.session_state.tags2, height=80)
        else:
            st.empty()

    with col3:
        if uploaded_files and st.session_state.selected_file:
            selected_file_obj = next(f for f in uploaded_files if f.name == st.session_state.selected_file)
            image = Image.open(selected_file_obj)
            st.image(image, caption=st.session_state.selected_file, width=300)

            st.subheader("Styl opisu")
            style = st.selectbox("Wybierz styl opisu", ["Techniczny", "Marketingowy", "Luźny"], key="style")

            st.subheader("Cechy do wygenerowania")
            features = st.multiselect("Co chcesz uwzględnić?", ["Kolory", "Obiekty", "Styl", "Emocje"], key="features")

            if st.button("Generuj opis i tagi"):
                with st.spinner("Generowanie..."):
                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format='PNG')
                    image_bytes = image_bytes.getvalue()

                    result = analyze_via_api(image_bytes, style, features)
                    tags = result.get("tags", [])
                    desc = result.get("description", "(brak opisu)")

                    tags1 = ', '.join(tags[:len(tags)//2])
                    tags2 = ', '.join(tags[len(tags)//2:])

                    st.session_state.description = desc
                    st.session_state.tags1 = tags1
                    st.session_state.tags2 = tags2
                    st.session_state.generated = True
                    
                    st.session_state.results[st.session_state.selected_file] = {
                        "description": desc,
                        "tags1": tags1,
                        "tags2": tags2,
                        "image_bytes": image_bytes
                    }


    if st.session_state.results:
        if st.button("Pobierz paczkę zip"):
            with tempfile.TemporaryDirectory() as temp_dir:
                meta = {}
                img_folder = os.path.join(temp_dir, "images")
                os.makedirs(img_folder, exist_ok=True)

                for fname, data in st.session_state.results.items():
                    img_id = f"{uuid.uuid4()}.png"
                    with open(os.path.join(img_folder, img_id), "wb") as f:
                        f.write(data["image_bytes"])

                    meta[img_id] = {
                        "description": data["description"],
                        "tags1": data["tags1"],
                        "tags2": data["tags2"]
                    }

                with open(os.path.join(temp_dir, "metadata.json"), "w") as f:
                    json.dump(meta, f, indent=2)

                zip_path = os.path.join(temp_dir, "package.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, arcname=os.path.relpath(file_path, temp_dir))

                with open(zip_path, "rb") as f:
                    st.download_button("Pobierz ZIP", f, file_name="tagi_i_opisy.zip")

with tabs[1]:
    question = st.text_input("Zadaj pytanie")
    if st.button("Zapytaj") and question:
        with st.spinner("Generowanie odpowiedzi..."):
            result = faq_via_api(question)
            answer = result["response"]
            st.session_state.faq_history.append((question, answer))

    for q, a in reversed(st.session_state.faq_history):
        st.markdown(f"**Pytanie:** {q}")
        st.markdown(f"**Odpowiedź:** {a}")
        st.markdown("---")
