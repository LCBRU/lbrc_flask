from lbrc_flask.forms.dynamic import FieldType


def test__field__format_value__integer(client, faker):
    ft = FieldType.get_integer()
    f = faker.field().get(field_type=ft)

    assert f.format_value(1_000_000) == '1,000,000'


def test__field__format_value__boolean(client, faker):
    ft = FieldType.get_boolean()
    f = faker.field().get(field_type=ft)

    assert f.format_value(True) == 'Yes'


def test__field__format_value__string(client, faker):
    ft = FieldType.get_string()
    f = faker.field().get(field_type=ft)

    assert f.format_value('Hello') == 'Hello'