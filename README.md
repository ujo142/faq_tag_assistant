## System do tagowania zdjęć oraz odpowiadania na pytania FAQ korzystają z techniki Retrieval-Augmented Generation (RAG).
- FastAPI (backend)
- Streamlit (frontend)
- Google Cloud (storage + Vertex AI + Gemini Vision)
- FAISS + Sentence Transformers (wektoryzacja i wyszukiwanie pytań)


## Opis poszczególnych modułów

| **Plik**                 | **Funkcja** |
|--------------------------|-------------|
| `api_server.py`          | Główne API (FastAPI). Obsługuje analizę obrazu (`/analyze`) i wyszukiwanie odpowiedzi FAQ (`/faq`). |
| `app.py`                 | Frontend w Streamlit — umożliwia użytkownikowi wgrywanie obrazów, generowanie opisów i tagów oraz zadawanie pytań FAQ. |
| `create_embeddings.py`   | Tworzy FAISS index na podstawie pytań z pliku `faq.json`. Używa SentenceTransformer do wektoryzacji. |
| `llm_vertex.py`          | Inicjalizuje klienta Google Vertex AI. |
| `rag_faq_engine.py`      | Ładuje FAISS index i metadane z Google Cloud Bucket oraz umożliwia wyszukiwanie podobnych pytań. |
| `vision.py`              | Korzysta z **Gemini Vision** do analizy obrazu i generowania opisu + tagów. |
| `requirements.txt`       | Lista zależności projektu. |
