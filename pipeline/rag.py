import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_vectorizer = None
_matrix = None
_guidelines = []

def _build_index():
    global _vectorizer, _matrix, _guidelines
    path = Path("knowledge_base/category_guidelines.json")
    _guidelines = json.loads(path.read_text())
    texts = [
        f"{g['category']} {g['tone']} {' '.join(g['key_attributes'])}"
        for g in _guidelines
    ]
    _vectorizer = TfidfVectorizer()
    _matrix = _vectorizer.fit_transform(texts)

def retrieve(query: str) -> dict:
    if _vectorizer is None:
        _build_index()
    q_vec = _vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _matrix)[0]
    return _guidelines[int(np.argmax(scores))]