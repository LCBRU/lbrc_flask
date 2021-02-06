from flask.helpers import url_for
import pytest
from lbrc_flask.pytest.asserts import assert__redirect, assert__requires_login
from flask_api import status
from lbrc_flask.pytest.helpers import login


def test__missing_route(client):
    resp = client.get("/uihfihihf")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


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

    assert resp.status_code == status.HTTP_200_OK


def test__get__requires_login__not(client):
    assert__requires_login(client, url_for("get_with_login"))

def test__get__requires_login__is(client, faker):
    login(client, faker)
    resp = client.get(url_for("get_with_login"))

    assert resp.status_code == status.HTTP_200_OK


def test__post__requires_login__not(client):
    assert__requires_login(client, url_for("post_with_login"), post=True)


def test__post__requires_login__is(client, faker):
    login(client, faker)
    resp = client.post(url_for("post_with_login"))

    assert resp.status_code == status.HTTP_200_OK


def test__post__no_login(client):
    resp = client.post(url_for("post_without_login"))
    assert__redirect(resp, url='http://localhost/')
