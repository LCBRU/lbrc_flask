from flask import flash
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    HiddenField,
)
from wtforms.validators import Length, DataRequired, Optional
from flask_wtf.file import FileAllowed


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


class FormBuilder:

    def __init__(self):
        self._fields = {}

    def get_form(self):
        class DynamicForm(FlashingForm):
            pass

        for name, field in self._fields.items():
            setattr(DynamicForm, name, field)

        return DynamicForm()

    def add_field(self, field):
        form_field = None

        kwargs = {"validators": [], "default": field.get_default()}

        if field.required:
            kwargs["validators"].append(DataRequired())
        else:
            kwargs["validators"].append(Optional())

        if field.max_length:
            kwargs["validators"].append(Length(max=field.max_length))

        if field.choices:
            kwargs["choices"] = field.get_choices()

        if field.allowed_file_extensions:
            kwargs["validators"].append(
                FileAllowed(
                    field.get_allowed_file_extensions(),
                    'Only the following file extensions are allowed "{}".'.format(
                        ", ".join(field.get_allowed_file_extensions())
                    ),
                )
            )

        module = __import__("wtforms")
        class_ = getattr(module, field.field_type.name)
        form_field = class_(field.field_name, **kwargs)

        self._fields[field.field_name] = form_field
