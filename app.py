# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv
import os

app = FastAPI(title="Bulgariko Search API")

# Разрешаваме CORS за всички домейни (можеш да ограничиш по-късно)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пътища към CSV файловете
INDEX_FILE = "search/complete_examples/advanced_pagerank_inverted_index.csv"
PAGERANK_FILE = "search/complete_examples/advanced_pagerank.csv"

inverted_index = {}
pagerank_scores = {}

# Ако CSV файловете ги няма, пускаме crawler + indexing
if not os.path.exists(INDEX_FILE) or not os.path.exists(PAGERANK_FILE):
    print("CSV files missing. Running crawler + indexing...")
    from search.complete_examples.advanced_pagerank import main as crawl_main
    crawl_main()
    print("Crawler finished.")

# Функция за зареждане на CSV файловете
def load_index():
    global inverted_index, pagerank_scores
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    term = row[0]
                    docs = row[1].split('|')
                    inverted_index[term] = docs
    else:
        print(f"WARNING: {INDEX_FILE} not found!")

    if os.path.exists(PAGERANK_FILE):
        with open(PAGERANK_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    pagerank_scores[row[0]] = float(row[1])
    else:
        print(f"WARNING: {PAGERANK_FILE} not found!")

load_index()

# Функция за търсене
def search(query: str):
    query = query.lower().split()
    results = {}
    for term in query:
        if term in inverted_index:
            for doc in inverted_index[term]:
                results[doc] = pagerank_scores.get(doc, 0)
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in sorted_results]

# API endpoint
@app.get("/search")
def search_api(q: str = Query(..., description="Your search query")):
    results = search(q)
    return {"query": q, "results": results[:10]}

# Стартиране на сървъра
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
