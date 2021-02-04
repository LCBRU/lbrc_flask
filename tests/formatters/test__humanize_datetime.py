from datetime import datetime
from lbrc_flask.formatters import humanize_datetime


def test__humanize_datetime__None():
    assert humanize_datetime(None) == ''

def test__humanize_datetime__Datetime():
    assert len(humanize_datetime(datetime.now())) > 0

