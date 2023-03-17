from flask import url_for
from lbrc_flask.pytest.helpers import login
from flask_api import status


def test__datalist__rendering(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('test_form'))
    assert resp.status_code == status.HTTP_200_OK

    dl = resp.soup.find("datalist", id="name_options")
    assert dl is not None
    
    opts = dl.find_all('option')
    assert len(opts) == 3

    assert [o["value"] for o in opts] == ['One', 'Two', 'Tree']


def test__datalist__posting(client, faker):
    user = login(client, faker)
    resp = client.post(url_for("test_form"))


def test__file__rendering(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('test_form'))
    assert resp.status_code == status.HTTP_200_OK

    fl = resp.soup.find("input", type="file")
    assert fl is not None
    assert fl['accept']=='.cdr,.png,.csv'


def test__unique_validator__is_unique(client, faker):
    user = login(client, faker)

    resp = client.post(url_for("test_form"), data={'last_name': faker.email()})
    assert resp.status_code == status.HTTP_200_OK

    assert resp.soup.find('h1', id="valid", text="True") is not None


def test__unique_validator__is_not_unique(client, faker):
    user = login(client, faker)

    resp = client.post(url_for("test_form"), data={'last_name': user.last_name})
    assert resp.status_code == status.HTTP_200_OK

    assert resp.soup.find('h1', id="valid", text="False") is not None
