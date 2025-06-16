import requests
from bs4 import BeautifulSoup
import feedparser
import re
from zoneinfo import ZoneInfo
from datetime import datetime
from search.contains_keyword import contains_keyword
from search.check_cache import check_cache
from search.format_date import format_date


def search_cnn(keyword, source, results, seen_links, url_blacklist):
    if source not in results:
        results[source] = []

    # RSS feed URLs
    rss_urls = ["http://rss.cnn.com/rss/cnn_tech.rss"]

    matched = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            full_url = entry.link
            pattern = r"/(\d{4})/(\d{2})/(\d{2})/"
            match = re.search(pattern, full_url)
            if match:
                year, month, day = match.groups()
                dt = datetime(int(year), int(month), int(day), tzinfo=ZoneInfo("America/New_York"))
                publish_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
            else:
                publish_date = "Unknown Date"

            date_array = format_date(publish_date)
            publish_date = date_array[0]
            epoch_time = date_array[1]

            summary = ""
            try:
                if title == '':
                    text = entry.summary
                    if ".\"" in text:
                        text = text.replace(".\"", "\".")
                    text = text.split('.')
                    title = str(text[0])
                    for x in text[1:]:
                        summary += str(x)

                if summary == "" or summary is None:
                    summary = entry.summary

            except Exception as e:
                print(f"[ERROR]: {title} = {e}")

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
                            # print(f"\n\n{soup}")

                            # Try a few common class names used by The Hacker News
                            article_body = soup.find('div', class_='articlebody') \
                                           or soup.find('div', class_='articlebody clear cf') \
                                           or soup.find('div', id='articlebody')

                            if article_body:
                                # Find the first <p> tag, even if nested
                                first_p_tag = article_body.find('p')
                                first_p = first_p_tag.get_text(strip=True) if first_p_tag else "No paragraph found."
                            else:
                                first_p = summary

                            seen_links.add(full_url)
                            matched.append((title, full_url, first_p, publish_date, epoch_time))
                        except Exception as e:
                            print(f"[ERROR] Failed to parse {full_url}: {e}")

        results[source] += matched

    return results

