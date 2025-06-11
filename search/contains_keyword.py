import re


def contains_keyword(text, keyword):
    pattern = r'\b' + re.escape(keyword) + r'\b'  # match only whole words
    if re.search(pattern, text, flags=re.IGNORECASE):
        return True
    return False
