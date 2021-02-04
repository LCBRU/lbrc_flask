from datetime import datetime
from lbrc_flask.formatters import format_datetime


def test__format_datetime__None():
    assert format_datetime(None) == ''

def test__format_datetime__Datetime():
    assert len(format_datetime(datetime.now())) > 0

