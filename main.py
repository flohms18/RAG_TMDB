import os
from dotenv import load_dotenv
import requests
import pandas as pd


load_dotenv()

API_KEY = os.getenv('API_KEY')


url = 'https://api.themoviedb.org/3/movie/popular'


headers = {
    "accept" : "application/json",
    "Authorization" : f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)




MyTMDB = pd.read_json(response.text)


print(MyTMDB)



