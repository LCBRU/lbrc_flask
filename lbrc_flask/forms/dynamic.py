from wtforms.validators import Length, DataRequired, Optional, Regexp
from flask_wtf.file import FileAllowed
from . import FlashingForm

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

        if field.validation_regex:
            kwargs["validators"].append(
                Regexp(
                    field.validation_regex,
                    message="Field is not of the correct format",
                )
            )

        module = __import__("wtforms")
        class_ = getattr(module, field.field_type.name)
        form_field = class_(field.get_label(), **kwargs)

        self._fields[field.field_name] = form_field
