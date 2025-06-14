import requests
from bs4 import BeautifulSoup
import feedparser
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
import re
from datetime import datetime


def search_cisa(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://us-cert.cisa.gov/ncas/alerts.xml"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        publish_date = entry.get("published", entry.get("updated", "Unknown Date"))

        # US-CERT date format is like: 'Tue, 27 Jun 2023 19:03:00 GMT'
        # Replace 'GMT' with '+0000' for timezone parsing
        publish_date = re.sub(r'EDT', '-0400', publish_date)

        # Convert to UTC and get epoch time
        if publish_date != "Unknown Date":
            dt = datetime.strptime(publish_date, "%a, %d %b %Y %H:%M:%S %z")
            epoch_time = int(dt.timestamp())
        else:
            epoch_time = 0

        first_p = check_cache(full_url)

        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                if first_p is not None:
                    seen_links.add(full_url)
                    matched.append((title, full_url, first_p, publish_date, epoch_time))
                else:
                    try:
                        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                        soup = BeautifulSoup(response.text, 'lxml')

                        # US-CERT alert pages often have content inside div with id='content' or 'main-content'
                        article_body = soup.find('div', id='content') or soup.find('div', id='main-content')

                        if article_body:
                            first_p_tag = article_body.find('p')
                            first_p = first_p_tag.get_text(strip=True) if first_p_tag else "No paragraph found."
                        else:
                            # fallback to summary from feed
                            first_p = entry.get('summary', 'No summary available.')

                        seen_links.add(full_url)
                        matched.append((title, full_url, first_p, publish_date, epoch_time))
                        print(matched)
                    except Exception as e:
                        print(f"[ERROR] Failed to parse {full_url}: {e}")

    results[source] += matched
    return results
