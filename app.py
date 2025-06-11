from flask import Flask, render_template, request, session, redirect
import threading
import webview
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = 'news-search'  # required for sessions
all_options = ['BBC', 'CNN', 'Reuters', 'TechCrunch']
url_blacklist = [
    "https://edition.cnn.com/markets",
    "https://edition.cnn.com/business/media",
    "https://edition.cnn.com/business/financial-calculators",
    'https://www.cnn.com/video',
    'https://edition.cnn.com?hpt=header_edition-picker',
'https://arabic.cnn.com?hpt=header_edition-picker',
]


def search_bbc(keyword, source, results, seen_links):
    if source not in results:
        results[source] = []

    urls = ["https://www.bbc.co.uk/news/"]
    urls.append("https://www.bbc.co.uk/news/technology")
    urls.append("https://www.bbc.co.uk/news/science_and_environment")
    urls.append("https://www.bbc.co.uk/news/business/economy")
    urls.append("https://www.bbc.co.uk/news/business")
    urls.append("https://www.bbc.co.uk/news/economy")
    urls.append("https://www.bbc.co.uk/news/world")

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

        full_url = "https://www.bbc.com" + href if href.startswith("/") else href

        # Use the URL to check for duplicates
        if keyword.lower() in text.lower() and full_url not in seen_links:
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

    results[source] += matched
    return results


def search_cnn(keyword, source, results, seen_links):
    if source not in results:
        results[source] = []

    urls = ["https://edition.cnn.com/business/tech"]
    urls.append("https://edition.cnn.com/search?q=cybersecurity&size=10&type=article&from=0&page=1&sort=newest&types=all&section=")
    urls.append("https://edition.cnn.com/search?q=artificial-intelligence&from=0&size=10&page=1&sort=newest&types=all&section=")
    urls.append("https://edition.cnn.com/search?q=cyber&section=us&from=0&size=10&page=1&sort=newest&types=all")
    urls.append("https://edition.cnn.com/search?q=cyber&section=world&from=0&size=10&page=1&sort=newest&types=all")

    soup = BeautifulSoup()
    for url in urls:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup.append(BeautifulSoup(response.text, "html.parser"))

    articles = soup.find_all("p")
    print(articles)

    articles = soup.find_all("a", href=True)

    matched = []
    for a in articles:
        text = a.get_text(strip=True)
        text = re.sub(r'Live Updates', 'LIVE ', text).strip()
        #text = re.sub(r',published at.*', '', text).strip()
        #text = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', text).strip()
        #text = re.sub(r'\d{1,2}:\d{2}', '', text).strip()
        #text = re.sub(r'Video.*', '', text).strip()
        #text = re.sub(r'Audio.*', '', text).strip()
        #text = re.sub(r'\d{1,2}\s*[ /-]\s*(January|February|March|April|May|June|July|August|September|October|November|December)', '', text, flags=re.IGNORECASE).strip()

        href = a['href']
        if not text or not href:
            continue

        full_url = "https://edition.cnn.com/" + href if href.startswith("/") else href

        # Use the URL to check for duplicates
        if full_url not in url_blacklist:
            if keyword.lower() in text.lower() and full_url not in seen_links:
                response = requests.get(full_url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, "html.parser")
                para = soup.find_all('p')
                index = 0
                first_p = ""
                for p in para:
                    if 2 <= index < 3:
                        first_p += f"{p.get_text(strip=True)} "

                    index += 1

                seen_links.add(full_url)
                matched.append((text, full_url, first_p))

    results[source] += matched
    return results


def news_search(keywords, source):
    results = {}
    seen_links = set()
    for keyword in keywords.split():
        print(f"\nSearching for Word: {keyword} in Source: {source}")

        if "BBC" in source:
            results = search_bbc(keyword, source, results, seen_links)

        if "CNN" in source:
            results = search_cnn(keyword, source, results, seen_links)

    return results


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", results=None, options=all_options,
                           sources=all_options)


def run_flask():
    app.run()


@app.route("/search", methods=["POST"])
def search():
    keywords = request.form.get("keyword")
    session['keywords'] = keywords
    sources = request.form.getlist("sources")
    session['selected_sources'] = sources
    print(f"Sources: {sources}")

    results = []
    for source in sources:
        raw_results = news_search(keywords, source)
        for source_name, articles in raw_results.items():
            for article in articles:
                title = article[0]
                full_url = article[1]
                snippet = article[2]
                results_dict = {"title": f"{source_name} - {title}", "snippet": f"{snippet}", "url": f"{full_url}"}
                results.append(results_dict)
                #print(results_dict)

    return render_template("index.html", results=results, options=all_options,
                           sources=sources, keywords=keywords)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("Flask App", "http://127.0.0.1:5000/")
    webview.start()
