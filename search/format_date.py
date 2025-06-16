import re
from datetime import datetime


def format_date(date):
    date_array = []
    date = re.sub(r'GMT', '+0000', date)
    date = re.sub(r'EDT', '-0400', date)
    date = re.sub(r'EST', '-0500', date)

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
