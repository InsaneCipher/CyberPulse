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
        publish_date = re.sub(r'EST', '-0500', publish_date)

        # Convert to UTC and get epoch time
        if publish_date != "Unknown Date":
            dt = datetime.strptime(publish_date, "%a, %d %b %Y %H:%M:%S %z")
            epoch_time = int(dt.timestamp())
        else:
            epoch_time = 0

        soup = BeautifulSoup(entry.summary, 'html.parser')
        paragraphs = soup.find_all('p')

        # Combine the first few paragraphs into a single string (adjust number as needed)
        if paragraphs:
            first_p = "\n\n".join(p.get_text() for p in paragraphs[1:2])
        else:
            first_p = soup.get_text(strip=True)[:500]  # fallback to raw text if no <p> tags

        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                seen_links.add(full_url)
                matched.append((title, full_url, first_p, publish_date, epoch_time))

    results[source] += matched
    return results
