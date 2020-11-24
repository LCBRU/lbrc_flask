from flask.helpers import url_for
import pytest
from tests import login
from lbrc_flask.database import db


def test__missing_route(client):
    resp = client.get("/uihfihihf")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "path, filename",
    [
        ('lbrc_flask.static', 'css/main.css'),
        ('lbrc_flask.static', 'img/cropped-favicon-32x32.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-192x192.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-180x180.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-270x270.png'),
        ('lbrc_flask.static', 'favicon.ico'),
        ('get_without_login', None),
    ],
)
def test__get__without_login(client, path, filename):
    resp = client.get(url_for(path, filename=filename))

    assert resp.status_code == 200


@pytest.mark.parametrize(
    "path, filename",
    [
        ("get_with_login", None),
    ],
)
def test__get__requires_login(client, path, filename):
    resp = client.get(url_for(path, filename=filename))
    assert resp.status_code == 302


@pytest.mark.parametrize(
    "path, filename",
    [
        ("post_with_login", None),
    ],
)
def test__post__requires_login(client, path, filename):
    resp = client.post(url_for(path, filename=filename))
    assert resp.status_code == 302


@pytest.mark.parametrize(
    "path, filename",
    [
        ("post_without_login", None),
    ],
)
def test__post__no_login(client, path, filename):
    resp = client.post(url_for(path, filename=filename))
    assert resp.status_code == 302
