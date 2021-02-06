from lbrc_flask.pytest.asserts import get_and_assert_standards
from flask import url_for
import pytest
from lbrc_flask.pytest.helpers import login


@pytest.mark.parametrize(
    "error_code", [404, 403, 500],
)
def test__standard_views(client, faker, error_code):
    user = login(client, faker)

    resp = get_and_assert_standards(client, url_for('give_me_error', error_code=error_code), user, has_navigation=False)
    assert resp.status_code == error_code
