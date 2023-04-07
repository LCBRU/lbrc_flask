from lbrc_flask.pytest.asserts import assert__error__required_field, assert__redirect
from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.forms.dynamic import FieldType
from flask_api import status


def test__flashing_form__rendering__error(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group(name='Hello')
    ft = FieldType.get_string()
    f = faker.get_test_field(field_group=fg, field_type=ft, required=True)


    resp = client.post(url_for('form', field_group_id=fg.id))
    assert resp.status_code == status.HTTP_200_OK
    assert__error__required_field(resp.soup, f.field_name)


def test__flashing_form__rendering__no_error(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group(name='Hello')
    ft = FieldType.get_string()
    f = faker.get_test_field(field_group=fg, field_type=ft)


    resp = client.post(url_for('form', field_group_id=fg.id))
    assert__redirect(resp, 'ui.index')


def test__flashing_form__has_no_value(client, faker):
    user = login(client, faker)
    resp = client.post(url_for("test_form"))

    assert resp.soup.find('h1', id="has_a_name", string="False") is not None
    assert resp.soup.find('h1', id="not_exists", string="False") is not None


def test__flashing_form__has_value(client, faker):
    user = login(client, faker)
    resp = client.post(url_for("test_form"), data={'name': 'fred'})

    assert resp.soup.find('h1', id="has_a_name", string="True") is not None
    assert resp.soup.find('h1', id="not_exists", string="False") is not None


def test__flashing_form__has_numeric_value(client, faker):
    user = login(client, faker)
    resp = client.post(url_for("test_form"), data={'name': '123'})

    assert resp.soup.find('h1', id="has_a_name", string="True") is not None
    assert resp.soup.find('h1', id="not_exists", string="False") is not None


def test__flashing_form__has_zero_value(client, faker):
    user = login(client, faker)
    resp = client.post(url_for("test_form"), data={'name': '0'})

    assert resp.soup.find('h1', id="has_a_name", string="False") is not None
    assert resp.soup.find('h1', id="not_exists", string="False") is not None
