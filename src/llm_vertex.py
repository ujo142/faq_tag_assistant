import os
import google.generativeai as genai
from dotenv import load_dotenv

from dotenv import load_dotenv
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def generate_vertex_response(question: str, similar: list, model_id="gemini-1.5-pro"):
    prompt = f"""
    Użytkownik zapytał: "{question}"

    Oto podobne pytania FAQ:
    {chr(10).join([f"- {q['question']}" for q in similar])}

    Odpowiedz jasno i rzeczowo.
    """
    model = genai.GenerativeModel(model_name=model_id)
    response = model.generate_content([prompt])
    return response.text.strip()
