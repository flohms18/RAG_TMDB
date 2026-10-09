from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests


from main import *


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
    best = torch.topk(compare, k=1)

    winner = best[1][0].tolist()

    jackpot = DF_TMDB.iloc[winner[0]].title

    return templates.TemplateResponse(request, 'home.html', {
        "text_request" : text_request,
        "jackpot" : jackpot
    }
    )
                      

