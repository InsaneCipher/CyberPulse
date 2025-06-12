import requests
from bs4 import BeautifulSoup
import feedparser
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache


def search_krebs(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    # Krebs on Security RSS feed URL
    rss_url = "https://krebsonsecurity.com/feed/"

    # Parse the RSS feed
    feed = feedparser.parse(rss_url)

    matched = []
    # Loop through each article entry
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
        first_p = check_cache(full_url)
        publish_date = entry.get("published", entry.get("updated", "Unknown date"))

        if full_url not in url_blacklist and full_url not in seen_links:
            if contains_keyword(title, keyword) or keyword.lower() == "*":
                if first_p is not None:
                    seen_links.add(full_url)
                    matched.append((title, full_url, first_p, publish_date))
                else:
                    # Fetch the article HTML
                    response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                    soup = BeautifulSoup(response.text, 'lxml')

                    # Try to find the first paragraph of the article
                    article_body = soup.find('div', class_='entry-content')  # Main content div
                    first_p = article_body.find('p').get_text()

                    seen_links.add(full_url)
                    matched.append((title, full_url, first_p, publish_date))

    results[source] += matched
    return results
