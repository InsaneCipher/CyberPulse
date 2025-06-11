import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from search.contains_keyword import contains_keyword


def search_bbc(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    urls = ["https://www.bbc.co.uk/news/",
            "https://www.bbc.co.uk/news/technology",
            "https://www.bbc.co.uk/news/science_and_environment",
            "https://www.bbc.co.uk/news/business/economy",
            "https://www.bbc.co.uk/news/business",
            "https://www.bbc.co.uk/news/economy",
            "https://www.bbc.co.uk/news/world"
            ]

    soup = BeautifulSoup()
    for url in urls:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup.append(BeautifulSoup(response.text, "html.parser"))

    articles = soup.find_all("a", href=True)

    matched = []
    for a in articles:
        text = a.get_text(strip=True)
        text = re.sub(r'Live\.', 'LIVE ', text).strip()
        text = re.sub(r',published at.*', '', text).strip()
        text = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', text).strip()
        text = re.sub(r'\d{1,2}:\d{2}', '', text).strip()
        text = re.sub(r'Video.*', '', text).strip()
        text = re.sub(r'Audio.*', '', text).strip()
        text = re.sub(r'\d{1,2}\s*[ /-]\s*(January|February|March|April|May|June|July|August|September|October|November|December)', '', text, flags=re.IGNORECASE).strip()

        href = a['href']
        if not text or not href:
            continue

        full_url = urljoin("https://www.bbc.com", href)

        # Use the URL to check for duplicates or blacklist
        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(text, keyword) or keyword.lower() == "*":
                response = requests.get(full_url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, "html.parser")
                para = soup.find_all('p')
                index = 0
                first_p = ""
                for p in para:
                    if index <= 1:
                        first_p += f"{p.get_text(strip=True)} "

                        index += 1

                seen_links.add(full_url)
                matched.append((text, full_url, first_p))
                print(full_url)

    results[source] += matched
    return results
