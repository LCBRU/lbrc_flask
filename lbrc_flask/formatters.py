import arrow
from datetime import datetime, date


def format_yesno(value):
    value = str(value)

    if value.lower() in ["false", "no", "0"]:
        return "No"
    elif value.lower() in ["true", "yes", "1"]:
        return "Yes"
    else:
        return ""


def format_datetime(value):
    if value:
        return value.strftime("%c")
    else:
        return ""


def humanize_datetime(value):
    if value:
        return arrow.get(value).to('Europe/London').humanize()
    else:
        return ""


def format_date(value):
    if value is None:
        return ''
    if value and (isinstance(value, date) or isinstance(value, datetime)):
        return value.strftime("%-d %b %Y")
    else:
        return value


def humanize_date(value):
    if value:
        return arrow.get(value).to('Europe/London').humanize(granularity="day")
    else:
        return ""


def format_currency(value):
    if value:
        return "£{:.2f}".format(value)
    else:
        return ""


def format_number(value):
    return "{:,}".format(value)
