# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv
import os

app = FastAPI(title="Bulgariko Search API")

# Разрешаваме CORS за твоя клиент
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with your client URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зареждаме индекса и PageRank
INDEX_FILE = "search/complete_examples/advanced_pagerank_inverted_index.csv"
PAGERANK_FILE = "search/complete_examples/advanced_pagerank.csv"

inverted_index = {}
pagerank_scores = {}

# Функция за зареждане на CSV файловете
def load_index():
    global inverted_index, pagerank_scores
    # Зареждаме inverted index
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    term = row[0]
                    docs = row[1].split('|')  # assume docs are | separated
                    inverted_index[term] = docs
    # Зареждаме PageRank
    if os.path.exists(PAGERANK_FILE):
        with open(PAGERANK_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    pagerank_scores[row[0]] = float(row[1])

load_index()

# Проста функция за търсене
def search(query: str):
    query = query.lower().split()
    results = {}
    for term in query:
        if term in inverted_index:
            for doc in inverted_index[term]:
                results[doc] = pagerank_scores.get(doc, 0)
    # Сортираме по PageRank
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in sorted_results]

# API крайна точка за търсене
@app.get("/search")
def search_api(q: str = Query(..., description="Your search query")):
    results = search(q)
    return {"query": q, "results": results[:10]}  # връщаме топ 10

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
