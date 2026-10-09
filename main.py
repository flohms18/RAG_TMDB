import os
from dotenv import load_dotenv
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer

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


embeddings = model.encode(DF_TMDB['overview'].to_list())

print(embeddings.shape)



