import datetime


def get_current_utc_timestamp() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp())
