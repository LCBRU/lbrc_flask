from flask import url_for
from lbrc_flask.pytest.helpers import login
import pytest
from lbrc_flask.forms.dynamic import FieldType
from flask_api import status
from lbrc_flask.pytest.asserts import assert__select
from rich import print


@pytest.mark.parametrize(
    "field_type_name", FieldType.all_field_type_name(),
)
def test__dynamic_form__rendering(client, faker, field_type_name):
    user = login(client, faker)

    fg = faker.get_test_field_group()
    ft = FieldType._get_field_type(field_type_name)
    f = faker.get_test_field(field_group=fg, field_type=ft)

    resp = client.get(url_for('form', field_group_id=fg.id))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.soup.find(ft.html_tag, type=ft.html_input_type, id=f.field_name) is not None


def test__select__rendering(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group()
    ft = FieldType.get_select()
    f = faker.get_test_field(field_group=fg, field_type=ft, choices='Once|Twice')

    resp = client.get(url_for('form', field_group_id=fg.id))
    assert resp.status_code == status.HTTP_200_OK

    assert__select(resp.soup, id=f.field_name, options=[('Once', 'Once'),('Twice', 'Twice')], multiselect=False)


def test__multiselect__rendering(client, faker):
    user = login(client, faker)

    fg = faker.get_test_field_group()
    ft = FieldType.get_multiselect()
    f = faker.get_test_field(field_group=fg, field_type=ft, choices='Once|Twice')

    resp = client.get(url_for('form', field_group_id=fg.id))
    assert resp.status_code == status.HTTP_200_OK

    assert__select(resp.soup, id=f.field_name, options=[('Once', 'Once'),('Twice', 'Twice')], multiselect=True)
