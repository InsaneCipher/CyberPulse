from flask import Flask, render_template, request, session
import threading
import webview
import re
from search.search_cnn import search_cnn
from search.search_bbc import search_bbc
from search.search_krebs import search_krebs
from search.search_thn import search_thn

app = Flask(__name__)
app.secret_key = 'news-search'  # required for sessions
all_options = ['BBC', 'CNN', 'Krebs', 'TheHackerNews', 'Reuters', 'TechCrunch']
with open("blacklist.txt", "r", encoding="utf-8") as f:
    url_blacklist = f.read().split("\n")


def contains_keyword(text, keyword):
    pattern = r'\b' + re.escape(keyword) + r'\b'  # match only whole words
    if re.search(pattern, text, flags=re.IGNORECASE):
        print(f"Found {keyword} in {text}")
        return True
    return False


def news_search(keywords, source):
    results = {}
    seen_links = set()
    for keyword in keywords.split():
        print(f"\nSearching for Word: {keyword} in Source: {source}")

        if "BBC" in source:
            results = search_bbc(keyword, source, results, seen_links, url_blacklist)

        if "CNN" in source:
            results = search_cnn(keyword, source, results, seen_links, url_blacklist)

        if "Krebs" in source:
            results = search_krebs(keyword, source, results, seen_links, url_blacklist)

        if "TheHackerNews" in source:
            results = search_thn(keyword, source, results, seen_links, url_blacklist)

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
    try:
        for source in sources:
            raw_results = news_search(keywords, source)
            for source_name, articles in raw_results.items():
                for article in articles:
                    title = article[0]
                    full_url = article[1]
                    snippet = article[2]
                    results_dict = {"title": f"{source_name} - {title}", "snippet": f"{snippet}", "url": f"{full_url}"}
                    results.append(results_dict)
                    print(results_dict)

    except SyntaxError as e:
        print(f"An exception occurred! \nError: {e}")

    return render_template("index.html", results=results, options=all_options,
                           sources=sources, keywords=keywords)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("Flask App", "http://127.0.0.1:5000/")
    webview.start()
