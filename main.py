import os
from dotenv import load_dotenv
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
load_dotenv()

API_KEY = os.getenv('API_KEY')


url = 'https://api.themoviedb.org/3/movie/popular'


headers = {
    "accept" : "application/json",
    "Authorization" : f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)



DF_TMDB = pd.DataFrame(response.json()["results"])

embeddings = model.encode(DF_TMDB['overview'].tolist())
query_emb = model.encode('A film about Odysseus')

smile = model.similarity(query_emb, embeddings)

best = torch.topk(smile, k=1)

answer = best[1][0].tolist()

print(DF_TMDB.iloc[answer].title)

