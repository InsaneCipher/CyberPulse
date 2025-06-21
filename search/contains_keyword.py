import re


def contains_keyword(text, keyword):
    # Split keyword string by spaces into list of keywords
    keywords = keyword.split()

    # Check that ALL keywords are found in text as whole words (case-insensitive)
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if not re.search(pattern, text, flags=re.IGNORECASE):
            return False

    return True
