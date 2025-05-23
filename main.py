from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from fastapi.middleware.cors import CORSMiddleware

class QueryInput(BaseModel):
    text: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = Word2Vec.load("w2v_model.model")
with open("embeddings.pkl", "rb") as f:
    data = pickle.load(f)

questions = data["questions"]
answers = data["answers"]
intents = data["intents"]
question_embeddings = np.array(data["question_embeddings"])

def embed_sentence(sentence):
    tokens = sentence.lower().split()
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    if not vectors:
        return np.zeros(model.vector_size)
    return np.mean(vectors, axis=0)

@app.get("/")
def root():
    return {"message": "Chatbot API with Word2Vec"}

@app.post("/predict")
def predict(query: QueryInput):
    q = query.text
    user_vec = embed_sentence(q).reshape(1, -1)
    scores = cosine_similarity(user_vec, question_embeddings)[0]
    best_idx = scores.argmax()
    best_score = scores[best_idx]

    return JSONResponse({
        "user_input": q,
        "matched_question": questions[best_idx],
        "matched_intent": intents[best_idx],
        "similarity_score": round(float(best_score), 3),
        "response": answers[best_idx]
    })
