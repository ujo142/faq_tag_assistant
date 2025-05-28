import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def analyze_image_with_vision(image_bytes, style, features):
    prompt = f"""
    Opisz to zdjęcie w stylu: {style}.
    Uwzględnij cechy: {', '.join(features)}.
    Zwróć opis i 2 listy tagów, każdą w osobnym bloku.
    Format:
    [OPIS]
    ...
    [TAGI 1]
    ...
    [TAGI 2]
    ...
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # lub "gemini-1.5-flash"


        # Przygotowanie obrazu do wysłania
        image_part = {
            "mime_type": "image/png",
            "data": image_bytes,
        }

        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [prompt, image_part]}
            ]
        )

        output = response.text.strip()
        desc = output.split("[OPIS]")[1].split("[TAGI 1]")[0].strip()
        tag1 = output.split("[TAGI 1]")[1].split("[TAGI 2]")[0].strip()
        tag2 = output.split("[TAGI 2]")[1].strip()

    except Exception as e:
        print("Błąd w generowaniu lub parsowaniu:", e)
        desc, tag1, tag2 = "(błąd parsowania)", "", ""

    return desc, tag1, tag2
