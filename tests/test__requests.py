import datetime
from flask import url_for
from lbrc_flask.pytest.helpers import login


def test__get_value_from_all_arguments__get(client, faker):
    login(client, faker)
    
    field_name = 'hello'
    value = 'jim'

    resp = client.get(url_for('json_requests', field_name=field_name, hello=value))

    assert resp.get_json()['result'] == value


def test__get_value_from_all_arguments__post(client, faker):
    login(client, faker)
    
    field_name = 'toast'
    value = 'jam'

    resp = client.post(url_for('json_requests', field_name=field_name), data={field_name: value})

    assert resp.get_json()['result'] == value


def test__get_value_from_all_arguments__post_json(client, faker):
    login(client, faker)
    
    field_name = 'bread'
    value = 'cheese'

    resp = client.post_json(url_for('json_requests', field_name=field_name), data={field_name: value})

    assert resp.get_json()['result'] == value
