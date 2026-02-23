import os
import threading
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

from flask import Flask, jsonify

# ------------------- NLTK setup -------------------
nltk.download("stopwords")
nltk.download("punkt")

# ------------------- Crawler -------------------
START_URLS = [
    "https://www.wikipedia.org/wiki/Google",
    "https://news.ycombinator.com/"
]

CRAWLED_DATA = []

def crawl_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        # simple tokenization
        words = word_tokenize(text)
        filtered_words = [w.lower() for w in words if w.isalpha() and w.lower() not in stopwords.words("english")]
        return filtered_words
    except Exception as e:
        print(f"Failed to crawl {url}: {e}")
        return None

def run_crawler():
    print("Crawler started...")
    for url in START_URLS:
        print(f"Crawling {url}")
        data = crawl_url(url)
        if data:
            CRAWLED_DATA.append({"url": url, "words": data})
        time.sleep(1)  # avoid spamming servers
    print("Crawler finished!")

# ------------------- Flask server -------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Crawler is running!"

@app.route("/data")
def data():
    return jsonify(CRAWLED_DATA)

if __name__ == "__main__":
    # run crawler in a background thread
    threading.Thread(target=run_crawler).start()
    
    # use Railway port or default 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
