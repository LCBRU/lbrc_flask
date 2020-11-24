import pytest
from flask import url_for
from lbrc_flask.pytest.helpers import login


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
    ],
)
def test__boilerplate__html_standards(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    assert resp.soup.html is not None
    assert resp.soup.html["lang"] == "en"
    assert resp.soup.head is not None
    assert (
        resp.soup.find(
            lambda tag: tag.name == "meta"
            and tag.has_attr("charset")
            and tag["charset"] == "utf-8"
        )
        is not None
    )
    assert resp.soup.title is not None
    assert resp.soup.body is not None


@pytest.mark.parametrize(
    "path, filename, requires_login",
    [
        ("security.login", None, False),
        ("security.forgot_password", None, False),
        ("security.change_password", None, True),
    ],
)
@pytest.mark.app_crsf(True)
def test__boilerplate__forms_csrf_token(client, faker, path, filename, requires_login):
    if requires_login:
        login(client, faker)

    resp = client.get(url_for(path, filename=filename))

    assert (
        resp.soup.find("input", {"name": "csrf_token"}, type="hidden", id="csrf_token")
        is not None
    )


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
    ],
)
def test__boilerplate__basic_navigation(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    resp.soup.nav is not None
    resp.soup.nav.find("a", href="/") is not None
    resp.soup.nav.find("a", string=user.full_name) is not None
    resp.soup.nav.find("a", string=user.full_name) is not None
    resp.soup.nav.find("a", href="/change") is not None
    resp.soup.nav.find("a", href="/logout") is not None
