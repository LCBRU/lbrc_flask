from datetime import datetime
from lbrc_flask.formatters import format_date


def test__format_date__None():
    assert format_date(None) == ''


def test__format_date__Datetime():
    assert len(format_date(datetime.now())) > 0


def test__format_date__Date():
    assert len(format_date(datetime.now().date())) > 0


def test__format_date__String(faker):
    expected = faker.pystr(min_chars=5, max_chars=10)
    assert format_date(expected) == expected
