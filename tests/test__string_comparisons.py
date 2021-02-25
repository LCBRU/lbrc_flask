import pytest
from lbrc_flask.string_functions import levenshtein_distance


@pytest.mark.parametrize(
    "string_a, string_b, expected",
    [
        ('book', 'bloke', 2),
        ('', '', 0),
        ('Levenshtein', 'Distance', 10),
        ('Distance', 'Levenshtein', 10),
        ('Distance', '', 8),
        ('', 'Levenshtein', 11),
    ],
)
def test_levenshtein_distance_examples(string_a, string_b, expected):
    assert levenshtein_distance(string_a, string_b) == expected