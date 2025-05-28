from fastapi import FastAPI, UploadFile, File
from vision import analyze_image_with_vision  
from google.cloud import storage
import faiss
import pickle
from fastapi import HTTPException
from pydantic import BaseModel
import traceback
from fastapi import Form
import json
from llm_vertex import generate_vertex_response
from rag_faq_engine import search_similar_questions
from rag_faq_engine import download_faq_index


class FAQQuery(BaseModel):
    question: str


def load_faiss_from_gcs(bucket_name="faq-tag-assistant-bucket"):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    index_blob = bucket.blob("faq.index")
    meta_blob = bucket.blob("faq_meta.pkl")

    index_blob.download_to_filename("tmp_faq.index")
    meta_blob.download_to_filename("tmp_meta.pkl")

    index = faiss.read_index("tmp_faq.index")

    with open("tmp_meta.pkl", "rb") as f:
        metadata = pickle.load(f)

    return index, metadata

def search_faq(query, index, metadata, model, top_k=3):
    query_emb = model.encode([query], normalize_embeddings=True)
    scores, ids = index.search(query_emb, top_k)

    results = []
    for i in ids[0]:
        results.append(metadata[i])

    return results


app = FastAPI()

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    style: str = Form(...),
    features: str = Form(...)  
):
    try:
        image_bytes = await file.read()
        feature_list = json.loads(features)
        result = analyze_image_with_vision(image_bytes, style, feature_list)

        description = result[0]
        tags = result[1].split(",") + result[2].split(",")

        return {"description": description, "tags": tags}

    except Exception as e:
        print("Błąd w analyze_image:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")


@app.post("/faq")
def handle_faq(query: FAQQuery):
    if not query.question:
        raise HTTPException(status_code=400, detail="Pytanie nie może być puste.")
    faq_index, faq_meta = download_faq_index()

    similar = search_similar_questions(query.question, faq_index, faq_meta)
    response = generate_vertex_response(query.question, similar)

    return {
        "question": query.question,
        "matches": similar,
        "response": response
    }
