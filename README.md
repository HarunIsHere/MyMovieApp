# Movie App 🎥 (SQL + OMDb API + HTML Generator)

A simple movie library application that lets you manage a movie collection from the command line, store it in SQLite (via SQLAlchemy), fetch movie data from the OMDb API, and generate a static website of your library.

## Features
- **SQL Storage (SQLite + SQLAlchemy)**
- **Add movie via OMDb API** (enter title only)
- **CRUD**
  - List movies
  - Add movie (API)
  - Delete movie
  - Update rating (kept for compatibility)
- **Analytics**
  - Stats (average/median/best/worst)
  - Random movie
  - Search / suggestions
  - Sort by rating / year
  - Filter by rating and year range
- **Website generation**
  - Generates `_static/index.html` from `_static/index_template.html`

## Project Structure
```text
Movie_SQL_HTML_API/
├─ movies.py
├─ storage/
│  ├─ __init__.py
│  └─ movie_storage_sql.py
├─ data/
│  └─ movies.db                (ignored by git)
├─ _static/
│  ├─ index_template.html
│  ├─ style.css
│  └─ index.html               (generated, ignored by git)
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## Setup

### 1) Create and activate a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

## OMDb API Key
This project uses the OMDb API to fetch movie data.

In `movies.py`, set:
```python
OMDB_API_KEY = "YOUR_KEY_HERE"
```

## Run the app
```bash
python3 movies.py
```

## Generate the website
1. Run the app
2. Choose menu option **12. Generate website**
3. The output file will be created at:
   - `_static/index.html`

Open that file in a browser (or preview it in Codio).

## Notes
- `data/movies.db` is runtime data and is not committed to git (see `.gitignore`).
- `_static/index.html` is generated output and is not committed to git.
