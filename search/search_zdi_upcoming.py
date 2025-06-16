import requests
from bs4 import BeautifulSoup
import feedparser
import hashlib
import re
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def search_zdi_upcoming(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://www.zerodayinitiative.com/rss/upcoming/"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        date_array = format_date(entry.get("published", entry.get("updated", "Unknown Date")))
        publish_date = date_array[0]
        epoch_time = date_array[1]

        # Generate pseudo-unique ID for this entry
        raw = f"ZDI: {title}|{publish_date}"
        unique_id = hashlib.md5(raw.encode()).hexdigest()

        soup = BeautifulSoup(entry.summary, 'html.parser')
        paragraphs = soup.find_all('p')

        # Combine the first few paragraphs into a single string (adjust number as needed)
        if paragraphs:
            first_p = "\n\n".join(p.get_text() for p in paragraphs[1:2])
        else:
            first_p = soup.get_text(strip=True)[:500]  # fallback to raw text if no <p> tags

        first_p = re.sub("AV.*", ".", first_p)

        if full_url not in url_blacklist and unique_id not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                seen_links.add(unique_id)
                matched.append((title, full_url, first_p, publish_date, epoch_time))

    results[source] += matched
    return results
