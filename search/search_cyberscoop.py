import re
import requests
from bs4 import BeautifulSoup
import feedparser
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def clean_html_paragraph(paragraph_html):
    # Remove all HTML tags and clean whitespace
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', paragraph_html)).strip()


def get_first_sentence(text):
    match = re.match(r'^(.+?[.!?]["\')]*)(\s|$)', text)
    return match.group(1).strip() if match else text.strip()


def search_cyberscoop(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    rss_url = "https://www.cyberscoop.com/feed/"
    feed = feedparser.parse(rss_url)

    matched = []
    for entry in feed.entries:
        title = entry.title
        full_url = entry.link
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

                        article_body = soup.find('div', class_='articlebody') \
                                    or soup.find('div', class_='articlebody clear cf') \
                                    or soup.find('div', id='articlebody')

                        if article_body:
                            first_p_tag = article_body.find('p')
                            raw_paragraph = str(first_p_tag) if first_p_tag else ""
                            cleaned = clean_html_paragraph(raw_paragraph)
                            first_p = get_first_sentence(cleaned)
                        else:
                            summary = entry.get("summary", "")
                            cleaned = clean_html_paragraph(summary)
                            first_p = get_first_sentence(cleaned)

                        seen_links.add(full_url)
                        matched.append((title, full_url, first_p, publish_date, epoch_time))
                    except Exception as e:
                        print(f"[ERROR] Failed to parse {full_url}: {e}")

    results[source] += matched
    return results
