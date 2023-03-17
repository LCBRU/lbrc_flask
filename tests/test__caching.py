import time
import pytest
from unittest.mock import patch

from lbrc_flask.caching import timed_cache

@pytest.fixture(scope="function")
def mock_y():
    with patch('tests.test__caching.y') as mock:
        yield mock


def test__timed_cache__result_correct(mock_y):
    time.sleep(1)
    x()
    mock_y.assert_called_once()


def test__timed_cache__called_twice_but_run_once(mock_y):
    time.sleep(1)
    x()
    x()
    mock_y.assert_called_once()


def test__timed_cache__cache_timed_out__called_again(mock_y):
    time.sleep(1)
    x()
    time.sleep(2)
    x()

    assert mock_y.call_count == 2


def test__timed_cache__cache_timed_out__caching_restarts(mock_y):
    time.sleep(1)
    x()
    time.sleep(2)
    x()
    x()

    assert mock_y.call_count == 2


@timed_cache(seconds=1)
def x():
    return y()

def y():
    return 3