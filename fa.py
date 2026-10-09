from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

from main import *


templates = Jinja2Templates(directory="templates")

app = FastAPI()

class TextArea (BaseModel):
    content : str

@app.get('/')
async def serve_home(request: Request):
    return templates.TemplateResponse(request, 'home.html')

@app.get('/API_call')
async def first(request: Request):
    everything = requests.get(url, headers=headers).json()
    return templates.TemplateResponse(request, 'home.html', {
            "everything" : everything
        })
    

