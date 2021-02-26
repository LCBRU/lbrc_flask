import datetime
from flask import url_for
from lbrc_flask.pytest.helpers import login


def test__json__posting(client, faker):
    u = login(client, faker)

    expected = 43

    resp = client.post_json(url_for('json'), data={
        'string': '10-Apr-2002',
        'integer': expected,
        'datetime': datetime.datetime.now(),
        'date': datetime.datetime.now().date(),
    })
    print(resp.get_json())
    assert resp.get_json()['result'] == expected
