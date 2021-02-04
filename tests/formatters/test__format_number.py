from lbrc_flask.formatters import format_number


def test__format_number__Small():
    assert format_number(2) == '2'


def test__format_number__LessThanAThousand():
    assert format_number(999) == '999'


def test__format_number__AThousand():
    assert format_number(1035) == '1,035'


def test__format_number__Millions():
    assert format_number(12_030_234) == '12,030,234'
