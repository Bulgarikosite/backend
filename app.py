import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ------------------- NLTK setup -------------------
nltk_data_path = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_data_path)

try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords", download_dir=nltk_data_path)
    nltk.download("punkt", download_dir=nltk_data_path)

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
        words = word_tokenize(text)
        filtered_words = [w.lower() for w in words if w.isalpha() and w.lower() not in stopwords.words("english")]
        return filtered_words
    except Exception as e:
        print(f"Failed to crawl {url}: {e}")
        return None

def run_crawler():
    while True:  # run continuously
        print("Crawler started...")
        for url in START_URLS:
            print(f"Crawling {url}")
            data = crawl_url(url)
            if data:
                CRAWLED_DATA.append({"url": url, "words": data})
            time.sleep(1)
        print("Crawler finished, sleeping 5 min...")
        time.sleep(300)  # wait 5 minutes before next crawl

# ------------------- Flask -------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Crawler is running!"

@app.route("/data")
def data():
    try:
        return jsonify(CRAWLED_DATA)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # start crawler in a thread
    threading.Thread(target=run_crawler, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
