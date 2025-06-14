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
from search.search_cisa import search_cisa
from search.search_crowdstrike import search_crowdstrike

app = Flask(__name__)
app.secret_key = 'news-search'  # required for sessions
all_options = ['BBC', 'CNN', 'Krebs', 'TheHackerNews', 'CyberScoop', 'SecurityWeek', 'Microsoft', 'Threatpost', 'CISA', 'CrowdStrike']
with open("blacklist.txt", "r", encoding="utf-8") as f:
    url_blacklist = f.read().split("\n")

with open('settings.json', 'r') as f:
    settings = json.load(f)

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

    if "CISA" in source:
        results = search_cisa(keyword, "US-CERT (CISA)", results, seen_links, url_blacklist)

    if "CrowdStrike" in source:
        results = search_crowdstrike(keyword, source, results, seen_links, url_blacklist)

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
    return render_template("index.html", results=None, options=all_options,
                           sources=settings["sources"], keywords=settings["last_search"])


def run_flask():
    app.run()


@app.route("/search", methods=["POST"])
def search():
    keywords = request.form.get("keyword")
    session['keywords'] = keywords
    settings["last_search"] = keywords
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

    sources = request.form.getlist("sources")
    session['selected_sources'] = sources
    settings["sources"] = sources
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

    print(f"Sources: {sources}")

    results = []
    sorted_results = []
    try:
        for source in sources:
            raw_results = news_search(keywords, source)
            for source_name, articles in raw_results.items():
                for article in articles:
                    title = article[0]
                    full_url = article[1]
                    snippet = article[2]
                    date = article[3]
                    epoch = article[4]
                    results_dict = {"title": f"{source_name} - {title}", "snippet": f"{snippet}", "url": f"{full_url}", "date": f"{date}", "epoch": epoch}
                    results.append(results_dict)
                    print(results_dict)

        sorted_results = sorted(results, key=lambda x: int(x["epoch"]), reverse=True)

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

    return render_template("index.html", results=sorted_results, options=all_options,
                           sources=sources, keywords=keywords)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("NewsFinder", "http://127.0.0.1:5000/")
    # Add a simple back button (native GUI button)
    webview.start()
