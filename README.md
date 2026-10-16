# RAG App with TMDB

A FastAPI web app that recommends movies from a natural-language description.
It follows a RAG (Retrieval-Augmented Generation) pipeline:

1. **Load**: fetches popular movies from the TMDB API
2. **Embed**: turns each overview into a vector (`sentence-transformers/all-MiniLM-L6-v2`)
3. **Retrieve**: compares the user's request to the overviews and keeps the 5 closest movies
4. **Augment**: injects those 5 movies into the LLM prompt
5. **Generate**: the `gemma4` model (via Ollama) picks the best 3 and explains why

## Prerequisites

- **Python 3.10+** (developed with Python 3.14)
- **[Ollama](https://ollama.com/download)** installed locally
- **A TMDB account** to get an API access token

## Installation

### 1. Clone the project

```bash
git clone <repo-url>
cd RAG_TMDB
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

> `uvicorn` runs the server and `python-multipart` is required to read the form.

### 4. Set up the TMDB key

1. Create an account on [themoviedb.org](https://www.themoviedb.org/signup)
2. Go to **Settings > API** and request a key
3. Copy the **API Read Access Token** (the long string starting with `eyJ...`).
   This is **not** the short "API Key": the app sends the token in an `Authorization: Bearer` header.
4. Create a `.env` file at the project root:

```env
API_KEY=eyJhbGciOi...your_token...
```

> The `.env` file is ignored by Git (see `.gitignore`). Never commit it.

### 5. Install the Gemma model with Ollama

```bash
ollama pull gemma4
```

Ollama must be running in the background while you use the app.
The Ollama desktop app starts it automatically; otherwise:

```bash
ollama serve
```

## Run the app

From the project root (the `static/` and `templates/` folders are resolved relative to the current directory):

```bash
fastapi dev fa.py
```

or, with uvicorn directly:

```bash
uvicorn fa:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

> On first start, the embedding model (~90 MB) is downloaded from Hugging Face, so startup may take a moment.

## Usage

1. Describe the movie you're looking for in the search field (e.g. *a space adventure with a lonely robot*)
2. Click **Search**
3. The page shows:
   - **Gemma's pick**: the 3 movies chosen by the LLM, with an explanation
   - **Top matches**: the 5 closest movies with their similarity score
     (green ≥ 0.60, orange ≥ 0.50, white below)

## Project structure

```
RAG_TMDB/
├── fa.py                 # FastAPI app + RAG pipeline
├── requirements.txt      # Python dependencies
├── templates/
│   └── home.html         # Single page (form + results)
├── static/
│   ├── css/style.css     # Styles
│   └── fonts/            # JetBrains Mono font
├── .env                  # TMDB token (to create, not versioned)
└── .gitignore
```

## Troubleshooting

| Problem | Likely cause |
|---|---|
| `KeyError: 'results'` | TMDB token missing, invalid, or the v3 key was used instead of the *Read Access Token* |
| `ConnectionError` to `localhost:11434` | Ollama is not running (`ollama serve`) |
| `model 'gemma4:latest' not found` | The model hasn't been downloaded (`ollama pull gemma4`) |
| `Directory 'static' does not exist` | The server was started from a folder other than the project root |
| `Form data requires "python-multipart"` | Install `python-multipart` (or `fastapi[standard]`) |

## Limitations

- Only the **first page** of TMDB popular movies (20 movies) is used as the search base.
- Embeddings are recomputed on every request.
