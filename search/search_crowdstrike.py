import requests
from bs4 import BeautifulSoup
import feedparser
import re
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


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

        date_array = format_date(publish_date)
        publish_date = date_array[0]
        epoch_time = date_array[1]

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
