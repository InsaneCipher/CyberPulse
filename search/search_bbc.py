import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def search_bbc(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        date_array = format_date(entry.get("published", entry.get("updated", "Unknown Date")))
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
                        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                        soup = BeautifulSoup(response.text, 'lxml')

                        # Try a few common class names used by The Hacker News
                        article_body = soup.find('div', class_='articlebody') \
                                      or soup.find('div', class_='articlebody clear cf') \
                                      or soup.find('div', id='articlebody')

                        if article_body:
                            # Find the first <p> tag, even if nested
                            first_p_tag = article_body.find('p')
                            first_p = first_p_tag.get_text(strip=True) if first_p_tag else "No paragraph found."
                        else:
                            first_p = entry.summary

                        seen_links.add(full_url)
                        matched.append((title, full_url, first_p, publish_date, epoch_time))
                    except Exception as e:
                        print(f"[ERROR] Failed to parse {full_url}: {e}")

    results[source] += matched
    return results
