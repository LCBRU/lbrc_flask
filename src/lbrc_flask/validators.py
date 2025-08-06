import re
from datetime import datetime, date, UTC
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def standardise_nhs_number(nhs_number):
    return re.sub('[- ]', '', nhs_number or '')


def calculate_nhs_number_checksum(nhs_number):
    checkcalc = lambda sum: 11 - (sum % 11)

    char_total = sum(
        [int(j) * (11 - (i + 1)) for i, j in enumerate(nhs_number[:9])]
    )
    return str(checkcalc(char_total)) if checkcalc(char_total) != 11 else '0'


def is_invalid_nhs_number(nhs_number):
    # No NHS Number is not invalid
    if not nhs_number:
        return False

    nhs_number = standardise_nhs_number(nhs_number)

    # A valid NHS number must be 10 digits long
    if not re.search(r'^[0-9]{10}$', nhs_number):
        return True

    if calculate_nhs_number_checksum(nhs_number) != nhs_number[9]:
        return True

    return False


def is_invalid_uhl_system_number(uhl_system_number):
    if not uhl_system_number:
        return False

    if not re.search(r'^([SRFG]\d{7}|[U]\d{7}.*|LB\d{7}|RTD[\-0-9]*)$', uhl_system_number):
        return True

    return False


def parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    ansi_match = re.fullmatch(r'(?P<year>\d{4})[\\ -]?(?P<month>\d{2})[\\ -]?(?P<day>\d{2})(?:[ T]\d{2}:\d{2}:\d{2})?(?:\.\d+)?(?:[+-]\d{2}:\d{2})?', value)
    if ansi_match:
        return date(
            int(ansi_match.group('year')),
            int(ansi_match.group('month')),
            int(ansi_match.group('day')),
        )

    parsed_date = parse(value, dayfirst=True)

    return parsed_date.date()


def parse_date_or_none(value):
    try:
        return parse_date(value)
    except:
        return None


def is_invalid_dob(dob):
    if not dob:
        return False

    if isinstance(dob, datetime):
        dob = dob.date()

    return dob < (datetime.now(UTC).date() - relativedelta(years=130)) or dob > datetime.now(UTC).date()


def standardise_postcode(postcode):
    if not postcode:
        return ''

    p = postcode.upper().replace(' ', '')
    return "{} {}".format(p[0:-3], p[-3:]).strip()


def is_invalid_postcode(postcode):
    if not postcode:
        return False

    if not re.search(r'^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s[0-9][A-Za-z]{2})$', postcode):
        return True

    return False


def is_number(s):
    """ Returns True if string is a number. """
    if re.match(r"^\d+?\.\d+?$", s) is None:
        return s.isdigit()
    return True


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def is_float(n):
    try:
        float(n)
        return True
    except ValueError:
        return False


def is_invalid_doi(doi):
    if not doi:
        return False

    if not re.search(r'^(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)$', doi):
        return True

    return False


