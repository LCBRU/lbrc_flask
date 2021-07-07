import markdown
from flask import flash
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    HiddenField,
    Field,
)
from wtforms.validators import Length, DataRequired
from wtforms.widgets import html_params
from flask_wtf.file import FileField as _FileField
from wtforms.widgets import FileInput as _FileInput


class DescriptionField(Field):

    def __init__(self, label=None, validators=None, description=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        if description is not None:
            self.description = description

    def widget(self, field, **kwargs):
        field_id = kwargs.pop('id', field.id)
        html = [u'<p {}>{}</p>'.format(html_params(id=field_id), markdown.markdown(field.description))]
        return u''.join(html)

    def process_formdata(self, data):
        pass


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


class SearchForm(FlashingForm):
    search = StringField("Search", validators=[Length(max=20)])
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


