from flask import Flask, render_template, request, session
import threading
import webview
import json
from dotenv import load_dotenv
import os
import argparse
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
from search.search_zdi_upcoming import search_zdi_upcoming
from search.search_zdi_published import search_zdi_published
from search.search_zdi import search_zdi
from search.search_dark_reading import search_dark_reading
from search.search_bleeping_computer import search_bleeping_computer
from search.search_the_record import search_the_record
from search.search_security_affairs import search_security_affairs
from search.search_ncsc import search_ncsc
from search.search_europol import search_europol
from search.search_fbi import search_fbi
from search.search_rapid7 import search_rapid7
from search.search_wired import search_wired
from search.search_kali import search_kali
from search.search_malwarebytes import search_malwarebytes
from search.search_palo_alto import search_palo_alto
from search.search_risky import search_risky
from search.search_eu_cert import search_eu_cert
from search.search_google_zero import search_google_zero
from search.search_japan_cert import search_japan_cert
from search.search_daily_swig import search_daily_swig
from search.search_darknet_diaries import search_darknet_diaries
from search.search_fortinet import search_fortinet
from search.search_vmware import search_vmware
from search.search_research_checkpoint import search_research_checkpoint
from search.search_security_boulevard import search_security_boulevard
from search.search_schneier import search_schneier
from search.search_ibm import search_ibm
from search.search_ncc import search_ncc
from search.search_trustedsec import search_trustedsec
from search.search_eset import search_eset
from search.search_kaspersky import search_kaspersky
from search.search_arstechnica import search_arstechnica
from search.search_realmode import search_realmode
from search.search_portswigger import search_portswigger
from search.search_mozilla import search_mozilla

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # required for sessions

source_groups = {
    "Mainstream News": [
        "BBC", "CNN", "Wired", "Ars Technica"
    ],

    "Cybersecurity Blogs": [
        "The Hacker News", "Threatpost", "Security Week", "CyberScoop",
        "Krebs On Security", "Zero Day Initiative Blog", "DarkReading",
        "Bleeping Computer", "Security Affairs", "The Record",
        "Google Project Zero", "Google Cloud Security Blog",
        "Security Boulevard", "The Daily Swig", "Schneier",
        "Realmode Labs", "NCC Group Research Blog", "TrustedSec Blog",
        "PortSwigger Research"
    ],

    "Vendors & Feeds": [
        "CrowdStrike", "Microsoft Security", "AWS Security", "ExploitDB",
        "Cisco Talos Intelligence", "SANS Internet Storm Center",
        "Zero Day Initiative: Upcoming", "Zero Day Initiative: Published",
        "Rapid7", "Malwarebytes", "Kali Linux", "Palo Alto Networks",
        "Check Point Research Blog", "Fortinet Blog", "VMware Security Blog",
        "IBM X‑Force", "Kaspersky Securelist", "ESET WeLiveSecurity",
        "Mozilla Security Blog"
    ],

    "Government & Law Enforcement": [
        "FBI Newsroom", "Europol Newsroom", "NCSC (UK)",
        "CERT-US (CISA)", "CERT-EU", "CERT-Japan"
    ],

    "Community & Aggregators": [
        "Substack – Risky Biz", "Darknet Diaries"
    ]
}

source_function_map = {
    "BBC": search_bbc,
    "CNN": search_cnn,
    "Krebs On Security": search_krebs,
    "The Hacker News": search_thn,
    "CyberScoop": search_cyberscoop,
    "Security Week": search_securityweek,
    "Microsoft Security": search_microsoft,
    "Threatpost": search_threatpost,
    "CERT-US (CISA)": search_cisa,
    "CrowdStrike": search_crowdstrike,
    "Google Cloud": search_cloudblog,
    "ExploitDB": search_exploit_db,
    "SANS Internet Storm Center": search_sans,
    "Cisco Talos Intelligence": search_cisco,
    "AWS Security": search_aws,
    "Zero Day Initiative: Upcoming": search_zdi_upcoming,
    "Zero Day Initiative: Published": search_zdi_published,
    "Zero Day Initiative Blog": search_zdi,
    "The Record": search_the_record,
    "Bleeping Computer": search_bleeping_computer,
    "DarkReading": search_dark_reading,
    "Security Affairs": search_security_affairs,
    "FBI Newsroom": search_fbi,
    "Europol Newsroom": search_europol,
    "NCSC (UK)": search_ncsc,
    "Wired": search_wired,
    "Rapid7": search_rapid7,
    "Palo Alto Networks": search_palo_alto,
    "Kali Linux": search_kali,
    "Malwarebytes": search_malwarebytes,
    "Substack – Risky Biz": search_risky,
    "CERT-EU": search_eu_cert,
    "CERT-Japan": search_japan_cert,
    "Google Project Zero": search_google_zero,
    "The Daily Swig": search_daily_swig,
    "Darknet Diaries": search_darknet_diaries,
    "Fortinet Blog": search_fortinet,
    "Security Boulevard": search_security_boulevard,
    "VMware Security Blog": search_vmware,
    "Check Point Research Blog": search_research_checkpoint,
    "Schneier": search_schneier,
    "IBM X‑Force": search_ibm,
    "NCC Group Research Blog": search_ncc,
    "TrustedSec Blog": search_trustedsec,
    "ESET WeLiveSecurity": search_eset,
    "Kaspersky Securelist": search_kaspersky,
    "Ars Technica": search_arstechnica,
    "Realmode Labs": search_realmode,
    "PortSwigger Research": search_portswigger,
    "Mozilla Labs": search_mozilla
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

    for source_key, search_func in source_function_map.items():
        if source_key in source:
            return search_func(keyword, source, results, seen_links, url_blacklist)

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
    app.run(debug=False, host="0.0.0.0", port=5000)


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
                           sources=sources, keywords=keywords, source_groups=source_groups,
                           source_count=str(len(sorted_results)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NewsFinder App")
    parser.add_argument('--nogui', action='store_true', help='Run without GUI (CLI mode)')
    args = parser.parse_args()

    if args.nogui:
        run_flask()
    else:
        threading.Thread(target=run_flask, daemon=True).start()
        webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
        webview.create_window("CyberScope", "http://127.0.0.1:5000/")
        webview.start()

