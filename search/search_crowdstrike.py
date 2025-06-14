import requests
from bs4 import BeautifulSoup
import feedparser
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
import re
from datetime import datetime


def search_crowdstrike(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://www.crowdstrike.com/en-us/blog/feed"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        title = re.sub(r'&.*;', '', title)
        full_url = entry.link
        publish_date = entry.get("published", entry.get("updated", "Unknown Date"))
        publish_date = re.sub(r'-', ' -', publish_date)

        # CrowdStrike uses a date format like: 'Tue, 11 Jun 2024 15:00:00 +0000'
        # so this should work for parsing:
        if publish_date != "Unknown Date":
            dt = datetime.strptime(publish_date, "%b %d, %Y %H:%M:%S %z")
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
                        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                        soup = BeautifulSoup(response.text, 'lxml')

                        # Try multiple selectors for main content
                        article_body = soup.find('div', class_='text text--blog-content') or \
                                       soup.find('div', class_='post-content') or \
                                       soup.find('article')

                        if article_body:
                            paragraphs = article_body.find_all('p')
                            if paragraphs:
                                # Join first 2 or 3 paragraphs as a summary
                                first_p = ' '.join(p.get_text(strip=True) for p in paragraphs[:1])
                            else:
                                first_p = "No paragraph found."
                        else:
                            first_p = entry.get('summary', 'No summary available.')

                        seen_links.add(full_url)
                        matched.append((title, full_url, first_p, publish_date, epoch_time))
                    except Exception as e:
                        print(f"[ERROR] Failed to parse {full_url}: {e}")

    results[source] += matched
    return results
