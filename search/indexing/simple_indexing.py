import re

def simple_index_page(webpage, webpage_url):
    
    #Collect title and description
    title_tag = webpage.find('title')
    title = title_tag.get_text().strip() if title_tag else 'No Title'
    
    #Collect description
    description = ''
    meta_description = webpage.find('meta', attrs={'name': 'description'})
    if meta_description and 'content' in meta_description.attrs:
        description = meta_description['content']
    else:
        text_content = webpage.get_text(separator=" ", strip=True)
        description = text_content[:200] + "..." if len(text_content) > 200 else text_content
    
    #Grab ALL the words in the page
    #regex disgusting...
    words = re.findall(r'\b\w+\b', webpage.get_text(separator=" ", strip=True).lower())
    
    #Double check and filter out any numbers, symbols, etc.
    #WE ONLY WANT WORDS
    words = [word for word in words if word.isalpha()]
    
    #Add the information to the index
    indexed_page = {
        "url": webpage_url,
        "title": title,
        "description": description,
        "words": words
    }
    print(f"Indexed: {webpage_url}. \n Here's the info:  \n title: {title} \n description: {description} \n number of words: {len(words)} \n")
    return indexed_page