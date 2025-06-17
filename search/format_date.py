import re
from datetime import datetime


def format_date(date):
    date_array = []

    iso_regex = re.compile(
        r'^\d{4}-\d{2}-\d{2}'  # Date: YYYY-MM-DD
        r'T'  # Separator 'T'
        r'\d{2}:\d{2}'  # Time: HH:MM (seconds optional)
        r'(:\d{2})?'  # Optional seconds :SS
        r'(?:\.\d+)?'  # Optional fractional seconds
        r'(Z|[+-]\d{2}:\d{2})$'  # Timezone: 'Z' or ±HH:MM
    )

    if bool(iso_regex.match(date)):
        dt = datetime.fromisoformat(date)
        date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")

    date = re.sub(r'GMT', '+0000', date)
    date = re.sub(r'EDT', '-0400', date)
    date = re.sub(r'EST', '-0500', date)
    date = re.sub(r'EST', '-0500', date)
    date = re.sub(r'CET', '+0100', date)
    date = re.sub(r'CEST', '+0200', date)
    date = re.sub(r'C-', '-', date)

    # Convert to UTC and get epoch time
    try:
        if date != "Unknown Date":
            dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
            epoch_time = int(dt.timestamp())
        else:
            epoch_time = 0
    except ValueError:
        if date != "Unknown Date":
            dt = datetime.strptime(date, "%b %d, %Y %H:%M:%S %z")
            epoch_time = int(dt.timestamp())
        else:
            epoch_time = 0

    date_array.append(date)
    date_array.append(epoch_time)

    return date_array
