from flask import url_for
from lbrc_flask.pytest.helpers import login


def test__security__get_user_id(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('user_id'))

    assert resp.get_json()['result'] == user.id
