import markdown
from flask import flash
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    HiddenField,
    Field,
    SelectMultipleField,
    BooleanField,
    SearchField,
)
from wtforms.validators import Length, DataRequired, ValidationError
from wtforms.widgets import html_params
from flask_wtf.file import FileField as _FileField
from wtforms.widgets import FileInput as _FileInput, ListWidget, CheckboxInput, HiddenInput

from lbrc_flask.data_conversions import ensure_list
from lbrc_flask.validators import is_integer


class HiddenBooleanField(BooleanField):
    widget = HiddenInput()


class DataListField(Field):
    choices = []

    def widget(self, field, **kwargs):
        field_id = kwargs.pop('id', field.id)
        options = ' '.join([f'<option {html_params(value=c)}>' for c in self.choices])
        return f'<datalist {html_params(id=field_id)}>{options}</datalist>'

    def process_formdata(self, data):
        pass


class ElementDisplayField(Field):

    def __init__(self, element_type='p', label=None, validators=None, description=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        if description is not None:
            self.description = description
        
        self._element_type = element_type

    def widget(self, field, **kwargs):
        field_id = kwargs.pop('id', field.id)
        html = [u'<{0} {1}>{2}</{0}>'.format(self._element_type, html_params(id=field_id), markdown.markdown(field.description))]
        return u''.join(html)

    def process_formdata(self, data):
        pass


class DescriptionField(ElementDisplayField):

    def __init__(self, label=None, validators=None, description=None, **kwargs):
        super().__init__('p', label, validators, description, **kwargs)


class FlashingForm(FlaskForm):
    def validate_on_submit(self):
        result = super(FlashingForm, self).validate_on_submit()

        if not result:
            for field, errors in self.errors.items():
                for error in errors:
                    flash(
                        "Error in the {} field - {}".format(
                            getattr(self, field).label.text, error
                        ),
                        "error",
                    )
        return result
    
    def has_value(self, field_name):

        if field_name not in self or field_name not in self.data:
            return False

        field = self[field_name]
        value = self.data[field_name]

        if isinstance(value, list):
            return len(value) > 0
    
        if value is None:
            return False

        if field.type in ['BooleanField']:
            return value

        if type(value) == str:
            if is_integer(value):
                return (int(value) != 0)

            if len(str(value)) == 0:
                return False

        return True
    

    def data_with_values(self):
        result = []
        strip_keys = ['page', 'csrf_token']

        for f in self:
            if f.name not in strip_keys and self.has_value(f.name):
                result.append(f)
        
        return result

    def raw_data_as_dict(self):
        return {f.name: f.raw_data for f in self.data_with_values()}

    def values_as_dict(self):
        result = {}

        for f in self.data_with_values():
            if f.type in ['MonthField']:
                result[f.name] =  f.data.strftime("%Y-%m")
                val = f.data.strftime("%Y-%m")
            elif f.type in ['BooleanField']:
                if f.data:
                    result[f.name] = f.data
            else:
                result[f.name] = f.data
    
        return result
    
    def values_description(self):
        result = {}
        for f in self.data_with_values():
            name = f.label.text
            datas = []
            for d in ensure_list(f.data):
                if f.choices:
                    choices = {str(k):v for k, v in dict(f.choices).items()}
                    datas.append(str(choices.get(str(d), str(d))))
                else:
                    datas.append(str(d))
                result[name] = ', '.join(datas)

        return result


class SearchForm(FlashingForm):

    def __init__(self, search_placeholder=None, **kwargs):
        super().__init__(**kwargs, meta={'csrf': False})

        if search_placeholder:
            self.search.render_kw = {"placeholder": search_placeholder}

    search = SearchField("Search", validators=[Length(max=100)])
    page = IntegerField("Page", default=1)


class ConfirmForm(FlashingForm):
    id = HiddenField("id", validators=[DataRequired()])


class FileInput(_FileInput):

    def __call__(self, field, **kwargs):
        if field.accept:
            kwargs[u'accept'] = ','.join(field.accept)
        return _FileInput.__call__(self, field, **kwargs)


class FileField(_FileField):
    widget = FileInput()

    def __init__(self, *args, **kwargs):
        self.accept = kwargs.pop('accept', None)
        super(FileField, self).__init__(*args, **kwargs)


class Unique(object):
    """ validator that checks field uniqueness """
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'this element already exists'
        self.message = message

    def __call__(self, form, field):         
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def boolean_coerce(value):
    value = str(value).lower()

    if value in ('true', 'yes'):
        return True
    elif value in ('false', 'no'):
        return False
    else:
        return ''
