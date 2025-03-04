from datetime import datetime


def extract_year(date_str: str) -> int:
    """Extracts the year from a date string.
    For unrealized trades, uses the current year.
    """
    if date_str != '0001-01-01 00:00:00':
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').year
    return datetime.now().year
