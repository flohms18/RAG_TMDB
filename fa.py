from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import ollama
from ollama import chat



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

load_dotenv()

API_KEY = os.getenv('API_KEY')

templates = Jinja2Templates(directory="templates")

app = FastAPI()

class TextArea (BaseModel):
    content : str



@app.get('/')
async def first(request: Request):
    
    return templates.TemplateResponse(request, 'home.html', {
        
            
        })
    

@app.post('/post_tmdb')
async def submit_form(request : Request, text_request : str = Form(...)):
    everything = requests.get(url,headers=headers).json()
    DF_TMDB = pd.DataFrame(everything['results'])
    emb = model.encode(DF_TMDB['overview'].tolist())

    query = model.encode(text_request)

    compare = model.similarity(query, emb)
    best = torch.topk(compare, k=5)

    winner = best[1][0].tolist()

    jackpot = DF_TMDB.iloc[winner[0]].title

    context = DF_TMDB.iloc[winner][['title', 'overview', 'release_date', 'vote_average']]

    LLM = f"""
            Pick the 3 movies that match the most with the user request.
            Use only the movies listed below and explain briefly why each one matches.

            Movies:
            {context.to_string()}

            User request:
            {text_request}
            """

    stream = chat(
    model='llama3.2:latest',
    messages=[{'role': 'user', 'content': LLM}]
)

    return templates.TemplateResponse(request, 'home.html', {
        "text_request" : text_request,
        "jackpot" : stream['message']['content']
    }
    )
                      

