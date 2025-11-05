from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import requests
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

load_dotenv()

# Initialize OpenRouter client for embeddings
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY'),
)

app = FastAPI(title="AttackGen API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmbedRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = 'mistralai/codestral-embed-2505'


class ContractAnalysisRequest(BaseModel):
    contractAddress: str
    etherscanApiKey: str
    topK: Optional[int] = 3
    embeddingsFile: Optional[str] = 'embeddings.json'


def create_embeddings(text: str, api_key: str = None, model: str = 'mistralai/codestral-embed-2505') -> List[float]:
    try:
        embedding = openrouter_client.embeddings.create(
            model=model,
            input=text[:7000],
            encoding_format="float"
        )
        return embedding.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def load_embeddings_from_file(input_file: str):
    with open(input_file, 'r') as f:
        embeddings = json.load(f)
    for emb in embeddings:
        emb['embedding'] = np.array(emb['embedding'])
    return embeddings


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed")
def embed(req: EmbedRequest):
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENROUTER_API_KEY or OPENAI_API_KEY not configured')
    vectors = [create_embeddings(t, api_key, req.model) for t in req.texts]
    return {"embeddings": vectors}


@app.post("/analyze-contract")
def analyze_contract(req: ContractAnalysisRequest):
    etherscan_url = (
        f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={req.contractAddress}&apikey={req.etherscanApiKey}"
    )
    r = requests.get(etherscan_url)
    data = r.json()
    if data.get('status') != '1' or not data.get('result'):
        raise HTTPException(status_code=400, detail='Failed to fetch contract data from Etherscan')

    src = data['result'][0].get('SourceCode', '')
    abi = data['result'][0].get('ABI', '')
    if not src or not abi:
        raise HTTPException(status_code=400, detail='Missing source code or ABI from Etherscan')

    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENROUTER_API_KEY or OPENAI_API_KEY not configured')
    combined = src + abi
    combined_vec = np.array(create_embeddings(combined, api_key))

    md_embs = load_embeddings_from_file(req.embeddingsFile)
    sims = []
    for chunk in md_embs:
        sim = float(cosine_similarity([combined_vec], [chunk['embedding']])[0][0])
        sims.append({"similarity": sim, "file": chunk['file'], "chunk_index": chunk['chunk_index']})

    sims.sort(key=lambda x: x['similarity'], reverse=True)
    top = sims[:req.topK]
    return {"top": top, "contractAddress": req.contractAddress}


@app.get("/")
def root():
    return {"message": "AttackGen FastAPI is running"}