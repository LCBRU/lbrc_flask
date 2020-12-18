from datetime import datetime, date

def format_yesno(value):
    if value is None:
        return ""
    elif value == "0":
        return "No"
    elif value == "False":
        return "No"
    elif value:
        return "Yes"
    else:
        return "No"

def format_datetime(value):
    if value:
        return value.strftime("%c")
    else:
        return ""

def format_date(value):
    if value is None:
        return ''
    if value and (isinstance(value, date) or isinstance(value, datetime)):
        return value.strftime("%-d %b %Y")
    else:
        return value

def format_currency(value):
    if value:
        return "£{:.2f}".format(value)
    else:
        return ""

def format_number(value):
    return "{:,}".format(value)
