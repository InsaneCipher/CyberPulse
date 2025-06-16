import requests
from bs4 import BeautifulSoup
import feedparser
import re
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def search_microsoft(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://www.microsoft.com/en-us/security/blog/feed/"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        summary = entry.summary
        first_p = check_cache(full_url)

        date_array = format_date(entry.get("published", entry.get("updated", "Unknown Date")))
        publish_date = date_array[0]
        epoch_time = date_array[1]

        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                if first_p is not None:
                    seen_links.add(full_url)
                    matched.append((title, full_url, first_p, publish_date, epoch_time))
                else:
                    try:
                        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                        soup = BeautifulSoup(response.text, 'lxml')

                        # Look for the <article> tag
                        article_tag = soup.find('article')
                        first_p = None

                        if article_tag:
                            # Try to find the first <p> with some real text (not just junk or empty)
                            for p in article_tag.find_all('p'):
                                text = p.get_text(separator=" ", strip=True)
                                if len(text) > 40:  # Avoid "Published on" or trivial sentences
                                    first_p = text
                                    break
                        # Fallback if paragraph extraction fails
                        if not first_p:
                            first_p = BeautifulSoup(summary, 'lxml').get_text(strip=True)

                        first_p = re.sub(r'The post.*', '', first_p)
                        seen_links.add(full_url)
                        matched.append((title, full_url, first_p, publish_date, epoch_time))
                    except Exception as e:
                        print(f"[ERROR] Failed to parse {full_url}: {e}")

    results[source] += matched
    return results
