from lbrc_flask.pytest.asserts import assert__search_html, get_and_assert_standards, assert__page_navigation
import pytest
from lbrc_flask.pytest.helpers import login
from flask import url_for


def test__boilerplate__html_standards(client, faker):
    user = login(client, faker)
    resp = get_and_assert_standards(client, url_for('ui.index'), user)


@pytest.mark.parametrize(
    "path, requires_login",
    [
        ("security.login", False),
        ("security.forgot_password", False),
        ("security.change_password", True),
    ],
)
@pytest.mark.app_crsf(True)
@pytest.mark.xfail
def test__boilerplate__forms_csrf_token(client, faker, path, requires_login):
    if not requires_login:
        user = faker.user().get()
    else:
        user = login(client, faker)

    resp = get_and_assert_standards(client, url_for(path), user, has_form=True, has_navigation=False)


@pytest.mark.app_crsf(True)
@pytest.mark.xfail
def test__boilerplate__search(client, faker):
    user = login(client, faker)
    resp = get_and_assert_standards(client, url_for('search'), user, has_form=True)
    print(resp.soup)
    assert__search_html(resp.soup, clear_url=url_for('search'))


@pytest.mark.parametrize(
    "item_count",
    [0, 1, 5, 6, 11, 16, 21, 26, 31, 101],
)
def test__boilerplate__pages(client, faker, item_count):
    user = login(client, faker)

    the_fields = [faker.field().get_in_db() for _ in range(item_count)]

    assert__page_navigation(client, 'pages_of_fields', {}, item_count)
