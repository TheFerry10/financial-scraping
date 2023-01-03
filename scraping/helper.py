def normalize_datetime(datetime_string: str) -> str:
    """
    Transform datetime string to normalized sql version:
    Example:
    30.01.2021 - 18:04 Uhr -> 2021-01-30 18:04:00
    """
    date, time = [x.strip() for x in datetime_string.split('-')]
    day, month, year = date.split('.')
    hour, minute = time.split(' ')[0].split(':')
    second = "00"
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"