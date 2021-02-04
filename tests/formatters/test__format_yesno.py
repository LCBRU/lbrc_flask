import pytest
from lbrc_flask.formatters import format_yesno


@pytest.mark.parametrize(
    ["input", "output"],
    [
        (None, ''),
        ('', ''),
        ("0", 'No'),
        (0, 'No'),
        ("False", 'No'),
        ("false", 'No'),
        (False, 'No'),
        (True, 'Yes'),
        ('True', 'Yes'),
        ('true', 'Yes'),
        ('1', 'Yes'),
        (1, 'Yes'),
    ],
)
def test__format_yesno__None(input, output):
    assert format_yesno(input) == output
