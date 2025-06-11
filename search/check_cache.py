import ast
from urllib.parse import urlparse


def normalize_url(url):
    # Normalize URL for comparison: lowercase + strip trailing slash
    if not url:
        return None
    parsed = urlparse(url.lower())
    normalized = parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip('/')
    return normalized


def check_cache(full_url):
    snippet = None
    norm_url = normalize_url(full_url)

    try:
        with open("results_cache.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                try:
                    data_dict = ast.literal_eval(line)
                except Exception:
                    # If line can't be parsed, skip it
                    continue

                cached_url = data_dict.get('url')
                if cached_url and normalize_url(cached_url) == norm_url:
                    snippet = data_dict.get('snippet')
                    return snippet
    except FileNotFoundError:
        pass  # Cache file doesn't exist yet

    return snippet
