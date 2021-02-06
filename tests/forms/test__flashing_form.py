from lbrc_flask.pytest.asserts import assert__error__required_field, assert__redirect
from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.forms.dynamic import FieldType
from flask_api import status


def test__dynamic_form__rendering__error(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group(name='Hello')
    ft = FieldType.get_string()
    f = faker.get_test_field(field_group=fg, field_type=ft, required=True)


    resp = client.post(url_for('form', field_group_id=fg.id))
    assert resp.status_code == status.HTTP_200_OK
    assert__error__required_field(resp.soup, f.field_name)


def test__dynamic_form__rendering__no_error(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group(name='Hello')
    ft = FieldType.get_string()
    f = faker.get_test_field(field_group=fg, field_type=ft)


    resp = client.post(url_for('form', field_group_id=fg.id))
    assert__redirect(resp, 'ui.index')
