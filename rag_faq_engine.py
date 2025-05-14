import faiss
import pickle
import tempfile
import numpy as np
from sentence_transformers import SentenceTransformer
from google.cloud import storage


BUCKET_NAME = "faq-tag-storage"
INDEX_BLOB = "faq.index"
META_BLOB = "faq_meta.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")  

def download_faq_index():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    tmp_index = tempfile.NamedTemporaryFile(delete=False)
    tmp_meta = tempfile.NamedTemporaryFile(delete=False)

    bucket.blob(INDEX_BLOB).download_to_filename(tmp_index.name)
    bucket.blob(META_BLOB).download_to_filename(tmp_meta.name)

    index = faiss.read_index(tmp_index.name)

    with open(tmp_meta.name, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata

def search_similar_questions(query, index, metadata, top_k=3):
    query_vec = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(query_vec, top_k)

    return [metadata[i] for i in indices[0]]