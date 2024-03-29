import datetime
from flask import url_for
from lbrc_flask.pytest.helpers import login
from flask_api import status


def test__json__posting(client, faker):
    u = login(client, faker)

    expected = 43

    resp = client.post_json(url_for('json'), data={
        'string': '10-Apr-2002',
        'integer': expected,
        'datetime': datetime.datetime.now(),
        'date': datetime.datetime.now().date(),
    })
    assert resp.get_json()['result'] == expected
    assert resp.status_code == status.HTTP_200_OK

def test__json__error(client, faker):
    u = login(client, faker)

    expected = 43

    resp = client.post_json(url_for('json'), data={
        'string': '10-Apr-2002',
        'integer': 'hgs',
        'datetime': datetime.datetime.now(),
        'date': datetime.datetime.now().date(),
    })
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
