from bs4 import BeautifulSoup
import requests
import time
import random

def sloth_bot():
    # our list of URLs to crawl 
    urls = ["https://en.wikipedia.org/wiki/Google"]
    visited_urls = set()
    #timer to see how long it takes to crawl
    start = time.time()
    #Loops through the list of urls
    CRAWL_LIMIT = 15
    current_crawl_count = 0

    while urls and current_crawl_count < CRAWL_LIMIT:
        # grabs the next url
        current_url = urls.pop(0)
        print("time to crawl: " + current_url)
        time.sleep(random.uniform(1, 3))
        try:
            response = requests.get(current_url)
            response.raise_for_status() 
        except requests.RequestException as e:
            print(f"Failed to retrieve {current_url}: {e}")
            continue
        
        # grabbing the content of the page
        webpage = BeautifulSoup(response.content, "html.parser")
    
        # grabbing the links from the page
        hyperlinks = webpage.select("a[href]")
        # looping through the links and adding them to our list of urls
        for hyperlink in hyperlinks:
            url = hyperlink["href"]
            #Formats the url into a proper url (don't worry about this)
            if url.startswith("#"):
                        continue  
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                base_url = "{0.scheme}://{0.netloc}".format(requests.utils.urlparse(current_url))
                url = base_url + url
            elif not url.startswith("http"):
                continue
            #
            url = url.split('#')[0]
            
            #if we haven't visited this url yet, add it to our list
            if url not in visited_urls:
                urls.append(url)
                visited_urls.add(url)

        current_crawl_count += 1
                
                
def main():
    # Start the crawling process
    sloth_bot()

if __name__ == "__main__":
    main()



