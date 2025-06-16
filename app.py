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
from search.search_cloudblog import search_cloudblog
from search.search_exploit_db import search_exploit_db
from search.search_sans import search_sans
from search.search_cisco import search_cisco
from search.search_aws import search_aws

app = Flask(__name__)
app.secret_key = 'news-search'  # required for sessions

source_groups = {
    "Mainstream News": ["BBC", "CNN"],
    "Cybersecurity Blogs": ["The Hacker News", "Threatpost", "Security Week", "CyberScoop", "Krebs On Security"],
    "Vendors & Feeds": ["US-CERT (CISA)", "CrowdStrike", "Microsoft Security", "Google Cloud", "AWS Security",
                        "ExploitDB", "Cisco Talos Intelligence", "SANS Internet Storm Center"]
}

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

    if "Krebs On Security" in source:
        results = search_krebs(keyword, source, results, seen_links, url_blacklist)

    if "The Hacker News" in source:
        results = search_thn(keyword, source, results, seen_links, url_blacklist)

    if "CyberScoop" in source:
        results = search_cyberscoop(keyword, source, results, seen_links, url_blacklist)

    if "Security Week" in source:
        results = search_securityweek(keyword, source, results, seen_links, url_blacklist)

    if "Microsoft Security" in source:
        results = search_microsoft(keyword, source, results, seen_links, url_blacklist)

    if "Threatpost" in source:
        results = search_threatpost(keyword, source, results, seen_links, url_blacklist)

    if "US-CERT (CISA)" in source:
        results = search_cisa(keyword, source, results, seen_links, url_blacklist)

    if "CrowdStrike" in source:
        results = search_crowdstrike(keyword, source, results, seen_links, url_blacklist)

    if "Google Cloud" in source:
        results = search_cloudblog(keyword, source, results, seen_links, url_blacklist)

    if "ExploitDB" in source:
        results = search_exploit_db(keyword, source, results, seen_links, url_blacklist)

    if "SANS Internet Storm Center" in source:
        results = search_sans(keyword, source, results, seen_links, url_blacklist)

    if "Cisco Talos Intelligence" in source:
        results = search_cisco(keyword, source, results, seen_links, url_blacklist)

    if "AWS Security" in source:
        results = search_aws(keyword, source, results, seen_links, url_blacklist)

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
    return render_template("index.html", results=None,
                           sources=settings["sources"], keywords=settings["last_search"],
                           source_groups=source_groups)


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

    return render_template("index.html", results=sorted_results,
                           sources=sources, keywords=keywords, source_groups=source_groups)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("NewsFinder", "http://127.0.0.1:5000/")
    # Add a simple back button (native GUI button)
    webview.start()
