# arXiv SearchEngine (Ging & Boogle)

<p align="center" style="display:flex; justify-content:center; gap:24px; align-items:center;">
  <img src="media/images/Ging_logo.svg" alt="Ging logo" width="400">
  <img src="media/images/Boogle_logo.svg" alt="Boogle logo" width="400">
</p>

## Overview

arXivSearchEngine is an educational search engine built around a subset of the arXiv corpus. It combines a simple inverted-index based retrieval implementation (in the `se/` package) with a small Django GUI for querying and comparing results to an external Solr instance. The project includes index creation, posting list management, ranking, a snippet generator and evaluation utilities for comparing results against Solr.

## Key features

- Create inverted indexes from a zipped JSON corpus (see `se/main.py`).
- Partial indexing with posting lists to control memory usage.
- Multiple search modes: single-term, phrase, multi-term and facetted (author/title/abstract).
- Snippet generation for returned documents.
- A small Django-based GUI to query the local engine and (optionally) compare results to a Solr instance.
- Evaluation metrics (precision@10, MAP, nDCG) implemented in `se/evaluation.py`.

## Quick facts / Contract

- Inputs: textual queries (plain keywords, phrase queries in quotes, facetted queries like `author:smith`).
- Outputs: ranked lists of document ids (and utilities to fetch document JSON records and snippets).
- Error modes: missing corpus, missing posting/index files, or Solr not running for Solr-based features.

## Requirements

- Python 3.8+ (the provided `requirements.txt` targets Python 3.x compatible packages).
- The packages listed in `requirements.txt` (Django, NLTK, numpy, requests, etc.).

Install dependencies into a virtual environment:

```bash
# from the project root
python -m venv .venv
source .venv/Scripts/activate   # on Windows Bash
pip install -r requirements.txt
```

Note: NLTK may require additional data downloads for tokenizers/stopwords. If you see NLTK errors, run a small Python session and download the required corpora, for example:

```python
import nltk
nltk.download('punkt')
```

## Setup (Django GUI)

1. Apply Django migrations and create a superuser if you want admin access:

```bash
python manage.py migrate
python manage.py createsuperuser
```

2. Run the development server:

```bash
python manage.py runserver
```

3. Open the GUI in your browser:

- Main local search interface: http://127.0.0.1:8000/
- Solr-based demo page: http://127.0.0.1:8000/ging

The GUI uses the internal `SearchEngine` (from `se/main.py`) to produce results and — optionally — compares them to a running Solr instance on `http://localhost:8983` for evaluation.

## Indexing & using the search engine (command-line)

Indexing and other core actions are implemented in `se/main.py` and related modules (`se/index.py`, `se/posting.py`, `se/search.py`). Typical actions include:

- Creating an index for a metadata field (e.g., `title`, `abstract`, `author`):

```bash
# Run from project root
python -c "from se.main import SearchEngine; s=SearchEngine(); s.create_index('title')"
```

- Search programmatically:

```python
from se.main import SearchEngine
s = SearchEngine()
ids = s.search('quantum entanglement')
data = s.get_info_by_id(ids)
```

- Generate the byte-offset dictionary (used by the project to map ids to JSON lines):

```bash
python -c "from se.main import SearchEngine; s=SearchEngine(); s.create_arxiv()"
```

Adjust the `se/settings.py` constants (paths, interval sizes, number-of-docs limits) to match your environment and dataset location.

## Solr integration

There is a `solr/` directory containing sample Solr config files (schema, stopwords, synonyms, and language resources). The project GUI can send queries to a Solr core named `inf_ret` at `http://localhost:8983/solr/inf_ret` for result comparison/evaluation.

To use Solr-based features you should:

1. Install and run Apache Solr (compatible with config files in `solr/conf/`).
2. Create a core named `inf_ret` and replace the core's `conf/` contents with files from this repo (or adapt as needed).
3. Start Solr and ensure it responds on port 8983.

If Solr is not running, the project will still work locally but features that contact Solr (evaluation and the `/ging` view) will fail.

## Project structure (important files)

- `manage.py` — Django entrypoint.
- `core/` — Django project settings and wsgi/asgi.
- `gui/` — small Django app for the web-based search interface and templates.
	- `gui/views.py` — logic that runs the local engine and optionally calls Solr.
	- `gui/templates/gui/index.html`, `ging.html` — UI templates.
- `se/` — the search engine implementation and utilities.
	- `se/main.py` — SearchEngine class: indexing, searching, snippet generation.
	- `se/index.py` — index building and posting-list creation.
	- `se/posting.py` — posting list helpers.
	- `se/search.py` — ranking and search algorithms.
	- `se/evaluation.py` — evaluation metrics for comparing to Solr results.
	- `se/settings.py` — paths and tunable constants used by the engine.
- `solr/` — example Solr configuration files and language-specific resources.
- `media/` — media files used by the web UI.

## Development notes & edge cases

- The indexer reads from a zipped JSON archive configured in `se/settings.py` (PATH_TO_ARCHIVE and PATH_TO_JSON). Make sure your corpus is present and the paths are correct.
- Indexing is done in batches controlled by `INTERVAL_OF_INSERTING` to limit memory use — tune this value for large corpora.
- The GUI and the CLI search both depend on the byte-offset mapping used by `get_info_by_id` to fetch JSON lines. If the mapping is missing or corrupted, look at `se/index.py` and `se/main.py:create_arxiv`.
- NLTK-based preprocessing may require downloading corpora (see Requirements section).
