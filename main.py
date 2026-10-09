import os
from dotenv import load_dotenv
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
from ollama import chat



model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
load_dotenv()

API_KEY = os.getenv('API_KEY')


url = 'https://api.themoviedb.org/3/movie/popular'


headers = {
    "accept" : "application/json",
    "Authorization" : f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)

User_Prompt = 'A film about Odysseus'

DF_TMDB = pd.DataFrame(response.json()["results"])

embeddings = model.encode(DF_TMDB['overview'].tolist())
query_emb = model.encode(User_Prompt)

smile = model.similarity(query_emb, embeddings)

best = torch.topk(smile, k=5)

answer = best[1][0].tolist()

context = DF_TMDB.iloc[answer][['title', 'overview', 'release_date', 'vote_average']]

LLM = f"""
Pick the 3 movies that match the most with the user request.
Use only the movies listed below and explain briefly why each one matches.

Movies:
{context.to_string()}

User request:
{User_Prompt}
"""

stream = chat(
    model='llama3.2:latest',
    messages=[{'role': 'user', 'content': LLM}]
)

print(stream['message']['content'])






