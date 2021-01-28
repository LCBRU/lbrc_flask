import re
from flask import url_for
from lbrc_flask.pytest.helpers import login
from flask_api import status


def _assert_html_standards(soup):
    assert soup.html is not None
    assert soup.html["lang"] == "en"
    assert soup.head is not None
    assert (
        soup.find(
            lambda tag: tag.name == "meta"
            and tag.has_attr("charset")
            and tag["charset"] == "utf-8"
        )
        is not None
    )
    assert soup.title is not None
    assert soup.body is not None


def _assert_csrf_token(soup):
    assert (
        soup.find("input", {"name": "csrf_token"}, type="hidden", id="csrf_token") is not None
    )


def _assert_basic_navigation(soup, user):
    assert soup.nav is not None
    assert soup.nav.find("a", href="/") is not None
    assert soup.nav.find("a", string=user.full_name) is not None
    assert soup.nav.find("a", href="/change") is not None
    assert soup.nav.find("a", href="/logout") is not None


def assert__html_standards(client, faker, path, user=None):
    if user is None:
        user = login(client, faker)

    resp = client.get(path)

    _assert_html_standards(resp.soup)
    _assert_basic_navigation(resp.soup, user)


def assert__form_standards(client, faker, path, user=None):
    if user is None:
        user = login(client, faker)

    resp = client.get(path)

    _assert_csrf_token(resp.soup)


def assert__error__message(soup, message):
    errors = "\n".join([d.text for d in soup.find_all("div", "alert")])
    rx = re.compile(message, re.IGNORECASE)
    assert rx.search(errors) is not None


def assert__error__required_field(soup, field_name):
    assert__error__message(soup, "Error in the {} field - This field is required.".format(field_name))


def assert__redirect(response, endpoint=None, url=None, **kwargs):
    assert response.status_code == status.HTTP_302_FOUND

    if endpoint:
        assert response.location == url_for(endpoint, _external=True, **kwargs)
    if url:
        assert response.location == url


def assert__requires_login(client, url, post=False):
    if post:
        resp = client.post(url)
    else:
        resp = client.get(url)

    assert__redirect(resp, 'security.login', next=url)


def assert__search_html(soup, clear_url):
    assert soup.find('input', id="search") is not None
    assert soup.find('a', string="Clear Search", href=clear_url) is not None
    assert soup.find('button', type="submit", string="Search") is not None


def assert__select(soup, id, options):
    select = soup.find('select', id=id)
    assert select is not None

    for o in options:
        assert select.find('option', value=o[0], string=o[1])


def get_and_assert_standards(client, url, user, has_form=False):
    resp = client.get(url)

    _assert_html_standards(resp.soup)
    _assert_basic_navigation(resp.soup, user)

    if has_form:
        _assert_csrf_token(resp.soup)

    return resp
