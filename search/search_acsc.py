import requests
from bs4 import BeautifulSoup
import feedparser
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def get_acsc_feed(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "max-age=0",
        "DNT": "1"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    return feed


def search_acsc(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://www.cyber.gov.au/rss/alerts"
    feed = get_acsc_feed(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        date_array = format_date(entry.get("published", entry.get("updated", "Unknown Date")))
        publish_date = date_array[0]
        epoch_time = date_array[1]

        try:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            paragraphs = soup.find_all('p')

            # Combine the first few paragraphs into a single string (adjust number as needed)
            if paragraphs:
                first_p = "\n\n".join(p.get_text() for p in paragraphs[1:2])
            else:
                first_p = soup.get_text(strip=True)[:500]  # fallback to raw text if no <p> tags
        except AttributeError:
            first_p = "No Summary Available"

        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                seen_links.add(full_url)
                matched.append((title, full_url, first_p, publish_date, epoch_time))

    results[source] += matched
    return results
