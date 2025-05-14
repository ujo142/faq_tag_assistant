import os
from google.genai import types as genai_types
from google.generativeai import GenerativeModel
from google.generativeai.types import Content, Part, Blob


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
        model = GenerativeModel("gemini-1.5-pro-vision")  

        contents = [
            Content(role="user", parts=[
                Part(text=prompt),
                Part(inline_data=Blob(mime_type="image/png", data=image_bytes))
            ])
        ]

        response = model.generate_content(contents)
        output = response.text.strip()

        desc = output.split("[OPIS]")[1].split("[TAGI 1]")[0].strip()
        tag1 = output.split("[TAGI 1]")[1].split("[TAGI 2]")[0].strip()
        tag2 = output.split("[TAGI 2]")[1].strip()

    except Exception as e:
        print("Błąd w generowaniu lub parsowaniu:", e)
        desc, tag1, tag2 = "(błąd parsowania)", "", ""

    return desc, tag1, tag2
