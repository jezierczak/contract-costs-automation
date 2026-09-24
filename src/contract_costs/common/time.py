from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

# Kontener Dockera chodzi w UTC – "dziś" i godziny harmonogramów liczymy
# jawnie w czasie polskim.
APP_TIMEZONE = ZoneInfo("Europe/Warsaw")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    return datetime.now(APP_TIMEZONE)


def local_today() -> date:
    return local_now().date()
