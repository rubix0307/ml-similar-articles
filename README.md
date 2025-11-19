# Semantic Similar Articles → Django + pgvector
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com)
[![pgvector](https://img.shields.io/badge/pgvector-0.4.1-orange)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Smart semantic search and recommendation of similar articles in a Django application.

## Key Features
- Chunking 500 tokens (100 tokens overlap)
- Model **intfloat/multilingual-e5-small** (384 dim, 100 languages)
- L2-normalization + **rounding embeddings to 4 decimal places** → compressing DB volume by 2–2.5x
- Storing all chunks in PostgreSQL via **pgvector**
- **HNSW-index** (m=16, ef_construction=256)
- Aggregation of similarity across all chunks of one article

## How It Works
1. Article → split into overlapping chunks (500/100)
2. Each chunk → 384-dim embedding → L2-normalization → rounding to 4 decimals
3. Saved in `ArticleEmbedding.embedding`
4. When displaying an article:
   - Take all its chunks
   - Perform ANN-search (HNSW + `<=>`) for each chunk
   - Aggregate similarities → get exact score for whole articles

## Installation
1. Set environment variables according to the example in `.env-example`.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py load_articles --take_count 1000`
5. `python manage.py embedding_article`
6. `python manage.py runserver`