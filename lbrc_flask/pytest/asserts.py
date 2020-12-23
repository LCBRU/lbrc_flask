import re
from lbrc_flask.pytest.helpers import login


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
    soup.nav is not None
    soup.nav.find("a", href="/") is not None
    soup.nav.find("a", string=user.full_name) is not None
    soup.nav.find("a", string=user.full_name) is not None
    soup.nav.find("a", href="/change") is not None
    soup.nav.find("a", href="/logout") is not None


def assert__html_standards(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    _assert_html_standards(resp.soup)
    _assert_basic_navigation(resp.soup, user)


def assert__form_standards(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    _assert_csrf_token(resp.soup)


def assert__error__message(soup, message):
    errors = "\n".join([d.text for d in soup.find_all("div", "alert")])
    rx = re.compile(message, re.IGNORECASE)
    assert rx.search(errors) is not None

def assert__error__required_field(soup, field_name):
    assert__error__message(soup, "Error in the {} field - This field is required.".format(field_name))
