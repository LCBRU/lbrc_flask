import datetime
from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.requests import add_parameters_to_url


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


def test__add_parameters_to_url__add_one(client, faker):
    t = add_parameters_to_url('https://example.com',{'fred': '1'})
    assert t == 'https://example.com?fred=1'


def test__add_parameters_to_url__add_two(client, faker):
    t = add_parameters_to_url('https://example.com',{'fred': '1', 'mary': '3'})
    assert t == 'https://example.com?fred=1&mary=3'

def test__add_parameters_to_url__add_to_existing(client, faker):
    t = add_parameters_to_url('https://example.com?tony=99',{'fred': '1', 'mary': '3'})
    assert t == 'https://example.com?tony=99&fred=1&mary=3'
