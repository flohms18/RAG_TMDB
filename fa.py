from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import requests
from ollama import chat
import os
from dotenv import load_dotenv
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
from fastapi.staticfiles import StaticFiles

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get('/')
async def first(request: Request):
    return templates.TemplateResponse(request, 'home.html', {


        })


# ============================================================
# RAG PIPELINE
#   1. LOAD       -> fetch the documents (movies) from TMDB
#   2. EMBED      -> convert every overview into a vector
#   3. RETRIEVE   -> embed the user user_query, find the 5 closest movies
#   4. AUGMENT    -> inject those 5 movies into the LLM prompt
#   5. GENERATE   -> the LLM answers using ONLY that context
# ============================================================
@app.post('/post_tmdb')
async def submit_form(request : Request, text_request : str = Form(...)):

    movie_stat = []

    # ---------- STEP 1 : LOAD ----------
    TMDB_DATA = requests.get(url,headers=headers).json()

    DF_TMDB = pd.DataFrame(TMDB_DATA['results'])

    # ---------- STEP 2 : EMBED ----------
    emb_tmdb = model.encode(DF_TMDB['overview'].tolist())

    # ---------- STEP 3 : RETRIEVE ----------
    user_query = model.encode(text_request)

    compare = model.similarity(user_query, emb_tmdb)

    best = torch.topk(compare, k=5)

    TOP_5 = best[1][0].tolist()
    context = DF_TMDB.iloc[TOP_5][['title', 'overview', 'release_date', 'vote_average', 'poster_path']]

    scores = best[0][0].tolist()

    for x in scores:
        round(x,2)


    for row, score in zip(context.itertuples(), scores):
        movie_stat.append({
            "title" : row.title,
            "release_date" : row.release_date,
            "score" : round(score, 2),
            "poster" : row.poster_path
        })

    # ---------- STEP 4 : AUGMENT ----------
    LLM = f"""
            Pick the 3 movies that match the most with the user request.
            Use only the movies listed below and explain briefly why each one matches.
            Give me the score of similary for each after the title
            Don't write bold text (** or *)
            Movies:
            {context.to_string()}

            User request:
            {text_request}

            Similarity Scores:
            {scores}
            """

    # ---------- STEP 5 : GENERATE ----------
    stream = chat(
    model='gemma4:latest',
    messages=[{'role': 'user', 'content': LLM}]
)

    return templates.TemplateResponse(request, 'home.html', {
        "text_request" : text_request,
        "movie_stat" : movie_stat,
        "jackpot" : stream['message']['content']
    }
    )


