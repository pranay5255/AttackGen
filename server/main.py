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

load_dotenv()

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
    model: Optional[str] = 'text-embedding-ada-002'


class ContractAnalysisRequest(BaseModel):
    contractAddress: str
    etherscanApiKey: str
    topK: Optional[int] = 3
    embeddingsFile: Optional[str] = 'embeddings.json'


def create_embeddings(text: str, api_key: str, model: str = 'text-embedding-ada-002') -> List[float]:
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "input": text[:7000],
        "model": model
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()['data'][0]['embedding']


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
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not configured')
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

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not configured')
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