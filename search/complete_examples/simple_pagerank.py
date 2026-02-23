from bs4 import BeautifulSoup
import requests
import time
import random
import csv
import sys
import os
# Add the root directory to sys.path
# This is to be able to import modules from other directories (indexing and serving) idk why...
# any imports from indexing/serving need to happen under this
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from indexing.simple_indexing import simple_index_page
from serving.pagerank import compute_pagerank

def sloth_bot():
    # Our list of URLs to crawl
    urls = ["https://en.wikipedia.org/wiki/Google"]
    visited_urls = set()
    
    # Create the index and graph
    index = {}  # URL -> page contents
    pagerank_graph = {}  # URL -> set of URLs it links to
    CRAWL_LIMIT = 5
    crawl_count = 0
        
    # Loops through the list of URLs
    while urls and crawl_count < CRAWL_LIMIT:
        # Grab the next URL
        current_url = urls.pop()
        if current_url in visited_urls:
            continue
        print("Time to crawl: " + current_url)
        time.sleep(random.uniform(1, 2))
        try:
            response = requests.get(current_url)
            response.raise_for_status() 
        except requests.RequestException as e:
            print(f"Failed to retrieve {current_url}: {e}")
            continue
        
        # Parse the content of the page
        webpage = BeautifulSoup(response.content, "html.parser")
        
        # Add the page to the index
        indexed_page = simple_index_page(webpage, current_url)
        index[current_url] = indexed_page
        visited_urls.add(current_url)
        
        # Grab the links from the page
        hyperlinks = webpage.select("a[href]")
        #This is where we store our connected pages
        hyperlink_connections = set()
        for hyperlink in hyperlinks:
            url = hyperlink["href"]
            # Format the URL into a proper URL
            if url.startswith("#"):
                continue  
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                base_url = "{0.scheme}://{0.netloc}".format(requests.utils.urlparse(current_url))
                url = base_url + url
            elif not url.startswith("http"):
                continue
            url = url.split('#')[0]
            #Add to the link connection
            hyperlink_connections.add(url)
            # If we haven't visited this URL yet, add it to our list
            if url not in visited_urls:
                urls.append(url)
        
        # Update the page's outgoing links
        index[current_url]['hyperlink_connections'] = hyperlink_connections
        pagerank_graph[current_url] = hyperlink_connections
        
        crawl_count += 1
        print(f"Crawled count: {crawl_count}, index size: {len(index)}, URLs left: {len(urls)}")
    
    # Compute PageRank
    pagerank_scores = compute_pagerank(pagerank_graph)
        
    """ This part is for saving the data to CSV files.
        However, if you don't want to save the data, you can remove/comment out this part.
        If you want to use a database, you can replace this part with a database connection.
    """
    
    with open('simple_pagerank.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["url", "title", "description", "pagerank", "words"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for url, info in index.items():
            writer.writerow({
                'url': url,
                'title': info['title'],
                'description': info['description'],
                'pagerank': pagerank_scores.get(url, 0),
                'words': ', '.join(info['words'])
            })



def main():
    # Start the crawling process
    sloth_bot()

if __name__ == "__main__":
    main()



