from datetime import datetime
from lbrc_flask.formatters import humanize_date


def test__humanize_date__None():
    assert humanize_date(None) == ''


def test__humanize_date__Datetime():
    assert len(humanize_date(datetime.now())) > 0


def test__humanize_date__Date():
    assert len(humanize_date(datetime.now().date())) > 0
