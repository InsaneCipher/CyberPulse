from flask import Flask, render_template, request, session
import threading
import webview
import json
from concurrent.futures import ThreadPoolExecutor
from search.search_cnn import search_cnn
from search.search_bbc import search_bbc
from search.search_krebs import search_krebs
from search.search_thn import search_thn
from search.search_cyberscoop import search_cyberscoop
from search.search_securityweek import search_securityweek
from search.search_microsoft import search_microsoft
from search.search_threatpost import search_threatpost

app = Flask(__name__)
app.secret_key = 'news-search'  # required for sessions
all_options = ['BBC', 'CNN', 'Krebs', 'TheHackerNews', 'CyberScoop', 'SecurityWeek', 'Microsoft', 'Threatpost']
with open("blacklist.txt", "r", encoding="utf-8") as f:
    url_blacklist = f.read().split("\n")

# Load cache
try:
    with open("results_cache.txt", "r", encoding="utf-8") as file:
        cache = set(line.strip() for line in file)
except FileNotFoundError:
    cache = set()


def run_search(keyword, source, results, seen_links):
    print(f"\nSearching for Word: {keyword} in Source: {source}")

    if "BBC" in source:
        results = search_bbc(keyword, source, results, seen_links, url_blacklist)

    if "CNN" in source:
        results = search_cnn(keyword, source, results, seen_links, url_blacklist)

    if "Krebs" in source:
        results = search_krebs(keyword, source, results, seen_links, url_blacklist)

    if "TheHackerNews" in source:
        results = search_thn(keyword, "The Hacker News", results, seen_links, url_blacklist)

    if "CyberScoop" in source:
        results = search_cyberscoop(keyword, source, results, seen_links, url_blacklist)

    if "SecurityWeek" in source:
        results = search_securityweek(keyword, "Security Week", results, seen_links, url_blacklist)

    if "Microsoft" in source:
        results = search_microsoft(keyword, "Microsoft Security", results, seen_links, url_blacklist)

    if "Threatpost" in source:
        results = search_threatpost(keyword, source, results, seen_links, url_blacklist)

    return results


def news_search(keywords, source):
    results = {}
    seen_links = set()

    # Launch all keyword searches in parallel
    with ThreadPoolExecutor(max_workers=min(8, len(keywords.split()))) as executor:
        futures = [executor.submit(run_search, keyword, source, results, seen_links) for keyword in keywords.split()]
        for future in futures:
            future.result()  # Wait for all to complete (and catch exceptions if needed)

    return results


@app.route("/", methods=["GET"])
def home():
    with open("options.txt", "r", encoding="utf-8") as f:
        saved_options = f.read().split("\n")
    return render_template("index.html", results=None, options=all_options,
                           sources=saved_options)


def run_flask():
    app.run()


@app.route("/search", methods=["POST"])
def search():
    keywords = request.form.get("keyword")
    session['keywords'] = keywords
    sources = request.form.getlist("sources")
    with open("options.txt", "w", encoding="utf-8") as f:
        for source in sources:
            f.write(source + "\n")
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

    # Write new results if not in cache
    with open("results_cache.txt", "a", encoding="utf-8") as file:
        for result in results:
            # Convert dict to a normalized JSON string (sorted keys to ensure consistency)
            normalized = json.dumps(result, sort_keys=True)

            if normalized not in cache:
                file.write(normalized + "\n")
                cache.add(normalized)  # Add immediately so no duplicates if looped again

    return render_template("index.html", results=results, options=all_options,
                           sources=sources, keywords=keywords)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("Flask App", "http://127.0.0.1:5000/")
    webview.start()
