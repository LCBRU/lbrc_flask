from lbrc_flask.formatters import format_currency


def test__format_currency__None():
    assert format_currency(None) == ''


def test__format_currency__NoPounds():
    assert format_currency(0.39) == '£0.39'


def test__format_currency__JustPennies():
    assert format_currency(0.02) == '£0.02'


def test__format_currency__Pounds():
    assert format_currency(1.02) == '£1.02'
