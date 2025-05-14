import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

# Załaduj FAQ
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

questions = [item["question"] for item in faq_data]

# Wektorowanie pytań
model = SentenceTransformer("all-MiniLM-L6-v2")  # lub inny BERT/PolBERT
embeddings = model.encode(questions, normalize_embeddings=True)

# Zbuduj FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # IP = cosine similarity (po normalizacji)
index.add(embeddings)

# Zapisz indeks i metadane
faiss.write_index(index, "faq.index")

with open("faq_meta.pkl", "wb") as f:
    pickle.dump(faq_data, f)
