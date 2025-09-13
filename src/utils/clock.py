from datetime import datetime
import pytz
import os

def local_tz():
    tz = os.getenv("LOCAL_TZ")
    if tz:
        try:
            return pytz.timezone(tz)
        except Exception:
            pass
    return datetime.now().astimezone().tzinfo

def now():
    return datetime.now(local_tz())

def today_str():
    return now().strftime("%Y-%m-%d")
