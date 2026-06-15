# Connecting This Project to Pinecone

How to wire Pinecone into this project (an Obsidian markdown wiki driven by Python
scripts like `scripts/wiki_tool.py`). The idea: turn each wiki note into a vector
embedding and store it in Pinecone so you can do semantic search / RAG over your notes.

## 1. Get credentials
- Sign up at pinecone.io → create a project → copy your **API key**.
- Decide on a cloud/region for a **serverless index** (e.g. `aws` / `us-east-1`).

## 2. Install the SDK
```bash
pip install pinecone        # core SDK (the package is now just "pinecone", not "pinecone-client")
pip install openai          # or whatever you use to generate embeddings
```
Add `pinecone` to a `requirements.txt` / `pyproject.toml` alongside your existing scripts.

## 3. Store the API key (don't hardcode)
Put it in an environment variable or `.env` (and make sure `.env` is in your `.gitignore`):
```
PINECONE_API_KEY=...
OPENAI_API_KEY=...
```

## 4. Initialize the client + create an index
The **`dimension` must match your embedding model** — e.g. OpenAI `text-embedding-3-small` = 1536 dims.
```python
import os
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])  # or just Pinecone() if env var is set

pc.indexes.create(
    name="clear-wiki",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)
index = pc.index("clear-wiki")
```

## 5. Embed your wiki notes and upsert them
The conceptual loop for your `Wiki/**/*.md` files:
```python
# 1. read each markdown note (optionally chunk long ones)
# 2. create an embedding for the text via your embedding model
# 3. upsert with the note path as the ID + useful metadata

index.upsert(vectors=[
    ("Wiki/Topics/llm-wiki.md", embedding, {"path": "...", "type": "topic"}),
])
```
Tip: use the file path (or a slug) as the vector **ID** so re-running the script updates
the same vector instead of duplicating it. Metadata (type, tags from your frontmatter,
folder) lets you filter queries later.

## 6. Query for semantic search / RAG
```python
q_emb = embed("how does the two-layer workflow work?")  # same model as ingest
results = index.query(vector=q_emb, top_k=5, include_metadata=True)
for m in results.matches:
    print(m.id, m.score)
```
Then feed the top matches' note text into an LLM prompt for RAG answers.

## How it fits this repo
- Most natural home: a new script like `scripts/wiki_embed.py` (ingest/sync) that walks
  the `Wiki/` tree, mirroring how `wiki_tool.py` already operates on those files.
- Run it on demand, or hook it into your existing `.githooks/pre-commit` flow to keep the
  index in sync as notes change.
- Your `catalog.jsonl` / `source-manifest.jsonl` could track which notes have been
  embedded and their content hash, so you only re-embed changed notes.

## Decide early
**Which embedding model** — its dimension is baked into the index at creation and can't be
changed afterward. Options: OpenAI, a local model, or Pinecone's built-in
inference / integrated embedding.
