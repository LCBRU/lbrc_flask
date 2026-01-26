import pytest
import re
from lbrc_flask.forms.dynamic import FieldType, FormBuilder
from wtforms.validators import Length, DataRequired, Optional, Regexp
from flask_wtf.file import FileAllowed


def build_form(field):
    out = FormBuilder()
    out.add_field(field)
    actual = out.get_form()()
    assert sum( 1 for f in actual) == 1
    field_actual = actual.__getattribute__(field.field_name)
    return field_actual


@pytest.mark.parametrize(
    ["x"],
    [
        (1,),
        (2,),
        (3,),
        (4,),
        (10,),
    ],
)
def test__add_field__field_added(client, faker, x):
    out = FormBuilder()

    for i in range(x):
        out.add_field(faker.field().get(save=True, order=i, name=str(i)))

    actual = out.get_form()()

    assert sum( 1 for f in actual) == x


@pytest.mark.parametrize(
    ["x"],
    [
        (1,),
        (2,),
        (3,),
        (4,),
        (10,),
    ],
)
def test__add_field_group__field_added(client, faker, x):
    out = FormBuilder()

    fg = faker.field_group().get(save=True)

    fg.fields = [faker.field().get(save=True) for _ in range(x)]

    out.add_field_group(fg)

    actual = out.get_form()()

    assert sum( 1 for f in actual) == x


@pytest.mark.parametrize(
    "field_type_name", FieldType.all_field_type_name(),
)
def test__add_field__correct_field_type_added(client, faker, field_type_name):
    field = faker.field().get(save=True, field_type=FieldType._get_field_type(field_type_name))

    field_actual = build_form(field)

    assert field_actual.type == field_type_name


def test__add_field__default_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_string())

    field_actual = build_form(field)

    assert field_actual.default is None


def test__add_field__default_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_integer())
    field.default = 3

    field_actual = build_form(field)

    assert field_actual.default == 3


def test__add_field__required_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_integer())
    field.required = True

    field_actual = build_form(field)

    assert any(True for v in field_actual.validators if isinstance(v, DataRequired))
    assert all(False for v in field_actual.validators if isinstance(v, Optional))


def test__add_field__required_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_integer())
    field.required = False

    field_actual = build_form(field)

    assert all(False for v in field_actual.validators if isinstance(v, DataRequired))
    assert any(True for v in field_actual.validators if isinstance(v, Optional))


def test__add_field__label_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_integer())
    field.label = 'Fred'

    field_actual = build_form(field)

    assert field_actual.label.text == 'Fred'


def test__add_field__label_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_integer())

    field_actual = build_form(field)

    assert field_actual.label.text == field.field_name


def test__add_field__maxlength_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_string())
    field.max_length = 30

    field_actual = build_form(field)

    length_validators = [v for v in field_actual.validators if isinstance(v, Length)]
    assert len(length_validators) == 1
    assert length_validators[0].max == 30


def test__add_field__maxlength_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_string())

    field_actual = build_form(field)

    assert all(False for v in field_actual.validators if isinstance(v, Length))


def test__add_field__choices_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_radio())
    field.choices = 'a|b|c'

    field_actual = build_form(field)

    assert field_actual.choices == [('a', 'a'), ('b', 'b'), ('c', 'c')]


def test__add_field__choices_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_radio())

    field_actual = build_form(field)

    assert field_actual.choices == []


def test__add_field__allowed_file_extensions_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_file())
    field.allowed_file_extensions = 'pdf|txt'

    field_actual = build_form(field)

    validators = [v for v in field_actual.validators if isinstance(v, FileAllowed)]
    assert len(validators) == 1
    assert validators[0].upload_set == ['pdf', 'txt']


def test__add_field__allowed_file_extensions_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_multifile(), allowed_file_extensions='')

    field_actual = build_form(field)

    validators = [v for v in field_actual.validators if isinstance(v, FileAllowed)]

    assert len(validators) == 0


def test__add_field__validation_regex_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_textarea())
    field.validation_regex = '^.*$'

    field_actual = build_form(field)

    validators = [v for v in field_actual.validators if isinstance(v, Regexp)]
    assert len(validators) == 1
    assert validators[0].regex == re.compile('^.*$')


def test__add_field__validation_regex_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_textarea())

    field_actual = build_form(field)

    assert all(False for v in field_actual.validators if isinstance(v, Regexp))


def test__add_field__description_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_description())
    field.description = 'Hello'

    field_actual = build_form(field)

    field_actual.description == 'Hello'


def test__add_field__description_not_set(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_description())

    field_actual = build_form(field)

    field_actual.description == ''


def test__add_field__description_is_None(client, faker):
    field = faker.field().get(save=True, field_type=FieldType.get_description())
    field.description = None

    field_actual = build_form(field)

    field_actual.description == ''
