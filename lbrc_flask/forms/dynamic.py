from wtforms.fields import IntegerField
from lbrc_flask.admin import AdminCustomView
from flask_admin.model.form import InlineFormAdmin
from wtforms import fields, validators
from wtforms.validators import Length, DataRequired, Optional, Regexp
from flask_wtf.file import FileAllowed
from lbrc_flask.database import db
from . import DescriptionField, FlashingForm
from ..formatters import format_boolean, format_number, format_yesno


class FieldType(db.Model):

    BOOLEAN = 'BooleanField'
    INTEGER = 'IntegerField'
    RADIO = 'RadioField'
    STRING = 'StringField'
    TEXTAREA = 'TextAreaField'
    FILE = 'FileField'
    MULTIPLE_FILE = 'MultipleFileField'
    DESCRIPTION = 'DescriptionField'
    SELECT = 'SelectField'
    MULTISELECT = 'SelectMultipleField'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    is_file = db.Column(db.Boolean)

    def format_value(self, value):
        if self.name == FieldType.INTEGER:
            strval = str(value)
            if value is None or not strval.isnumeric():
                return ''
            else:
                return format_number(int(strval))
        elif self.name == FieldType.BOOLEAN:
            return format_yesno(value)
        else:
            return value

    def data_value(self, value):
        if self.name == FieldType.BOOLEAN:
            return format_boolean(value)
        else:
            return value

    @property
    def html_tag(self):
        if self.name == FieldType.DESCRIPTION:
            return 'p'
        elif self.name == FieldType.RADIO:
            return 'ul'
        elif self.name == FieldType.TEXTAREA:
            return 'textarea'
        elif self.name in [FieldType.SELECT, FieldType.MULTISELECT]:
            return 'select'
        else:
            return 'input'

    @property
    def html_input_type(self):
        if self.name == FieldType.BOOLEAN:
            return 'checkbox'
        elif self.name == FieldType.INTEGER:
            return 'number'
        elif self.name == FieldType.STRING:
            return 'text'
        elif self.name == FieldType.FILE:
            return 'file'
        elif self.name == FieldType.MULTIPLE_FILE:
            return 'file'

    @property
    def is_boolean(self):
        return self.name == FieldType.BOOLEAN

    @property
    def is_select_multiple(self):
        return self.name == FieldType.MULTISELECT

    @property
    def is_textarea(self):
        return self.name == FieldType.TEXTAREA

    @property
    def has_choices(self):
        return self.name in [FieldType.MULTISELECT, FieldType.SELECT, FieldType.RADIO]

    @staticmethod
    def all_field_type_name():
        return [
            FieldType.BOOLEAN,
            FieldType.DESCRIPTION,
            FieldType.FILE,
            FieldType.INTEGER,
            FieldType.MULTIPLE_FILE,
            FieldType.RADIO,
            FieldType.STRING,
            FieldType.TEXTAREA,
            FieldType.SELECT,
            FieldType.MULTISELECT,
        ]

    @classmethod
    def _get_field_type(cls, name):
        return FieldType.query.filter_by(name=name).one()

    @classmethod
    def get_boolean(cls):
        return cls._get_field_type(FieldType.BOOLEAN)

    @classmethod
    def get_integer(cls):
        return cls._get_field_type(FieldType.INTEGER)

    @classmethod
    def get_radio(cls):
        return cls._get_field_type(FieldType.RADIO)

    @classmethod
    def get_string(cls):
        return cls._get_field_type(FieldType.STRING)

    @classmethod
    def get_textarea(cls):
        return cls._get_field_type(FieldType.TEXTAREA)

    @classmethod
    def get_file(cls):
        return cls._get_field_type(FieldType.FILE)

    @classmethod
    def get_multifile(cls):
        return cls._get_field_type(FieldType.MULTIPLE_FILE)

    @classmethod
    def get_description(cls):
        return cls._get_field_type(FieldType.DESCRIPTION)

    @classmethod
    def get_select(cls):
        return cls._get_field_type(FieldType.SELECT)

    @classmethod
    def get_multiselect(cls):
        return cls._get_field_type(FieldType.MULTISELECT)

    def __str__(self):
        return self.name


class FieldTypeSetup():
    def setup(self):
        self._add_field_type(FieldType(name=FieldType.BOOLEAN))
        self._add_field_type(FieldType(name=FieldType.INTEGER))
        self._add_field_type(FieldType(name=FieldType.RADIO))
        self._add_field_type(FieldType(name=FieldType.STRING))
        self._add_field_type(FieldType(name=FieldType.TEXTAREA))
        self._add_field_type(FieldType(name=FieldType.FILE, is_file=True))
        self._add_field_type(FieldType(name=FieldType.MULTIPLE_FILE, is_file=True))
        self._add_field_type(FieldType(name=FieldType.DESCRIPTION))
        self._add_field_type(FieldType(name=FieldType.SELECT))
        self._add_field_type(FieldType(name=FieldType.MULTISELECT))

    def _add_field_type(self, field_type):
        if FieldType.query.filter_by(name=field_type.name).count() == 0:
            db.session.add(field_type)


class FieldGroup(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))

    def __str__(self):
        return self.name

    def get_field_for_field_name(self, field_name):
        return {f.field_name: f for f in self.fields}.get(field_name)


class Field(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    field_group_id = db.Column(db.Integer(), db.ForeignKey(FieldGroup.id))
    field_group = db.relationship(FieldGroup, backref='fields')
    order = db.Column(db.Integer())
    field_type_id = db.Column(db.Integer(), db.ForeignKey(FieldType.id))
    field_type = db.relationship(FieldType, lazy="joined")
    field_name = db.Column(db.String(100))
    label = db.Column(db.String(500))
    required = db.Column(db.Boolean, default=0)
    reportable = db.Column(db.Boolean, default=0)
    max_length = db.Column(db.Integer(), default=0)
    default = db.Column(db.String(100), default="")
    choices = db.Column(db.String(1000), default="")
    allowed_file_extensions = db.Column(db.String(200), default="")
    download_filename_format = db.Column(db.String(200), default="")
    validation_regex = db.Column(db.String(200), default="")
    description = db.Column(db.UnicodeText, default="")

    def format_value(self, value):
        return self.field_type.format_value(value)

    def data_value(self, value):
        return self.field_type.data_value(value)

    def get_default(self):
        if self.default == '':
            return None
        else:
            return self.default

    @property
    def has_choices(self):
        return self.field_type.has_choices

    def get_choices(self):
        if self.field_type.is_boolean:
            return ['Yes', 'No']
        elif not self.choices:
            return []
        else:
            return [(c, c) for c in self.choices.split("|")]

    def get_allowed_file_extensions(self):
        return self.allowed_file_extensions.split("|")
    
    def get_label(self):
        if self.label:
            return self.label
        else:
            return self.field_name

    def __repr__(self):
        return 'Field(field_name="{}", order="{}", field_type="{}")'.format(
            self.field_name, self.order, self.field_type.name
        )

class FormBuilder:

    def __init__(self, field_group=None):
        self._fields = {}

        if field_group:
            self.add_field_group(field_group)

    def get_form(self):
        class DynamicForm(FlashingForm):
            pass

        for name, field in self._fields.items():
            setattr(DynamicForm, name, field)

        return DynamicForm
    
    def add_field_group(self, field_group):
        for f in sorted(field_group.fields, key=lambda x: x.order):
            self.add_field(f)

    def add_field(self, field):
        form_field = None

        kwargs = {"validators": [], "default": field.get_default()}

        if field.required:
            kwargs["validators"].append(DataRequired())
        else:
            kwargs["validators"].append(Optional())

        if field.max_length:
            kwargs["validators"].append(Length(max=field.max_length))

        if field.has_choices:
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

        if field.field_type == FieldType.get_description():
            form_field = DescriptionField(field.get_label(), description=field.description, **kwargs)
        else:
            module = __import__("wtforms")
            class_ = getattr(module, field.field_type.name)
            form_field = class_(field.get_label(), description=field.description, **kwargs)

        self.add_form_field(field.field_name, form_field)

    def add_form_field(self, field_name, form_field):
        self._fields[field_name] = form_field

# Initialisation

def init_dynamic_forms(app):
    pass

def create_field_types():
    FieldTypeSetup().setup()

    db.session.commit()


# Admin Forms

class FieldlineView(InlineFormAdmin):
    form_args = dict(
        field_name=dict(validators=[validators.DataRequired()]),
        order=dict(validators=[validators.DataRequired()]),
        field_type=dict(query_factory=lambda: FieldType.query.order_by(FieldType.name)),
    )


class FieldGroupView(AdminCustomView):
    form_args = dict(
        name=dict(validators=[validators.DataRequired()]),
    )
    form_columns = [
        FieldGroup.name,
    ]
    column_searchable_list = [FieldGroup.name]
    inline_models = (FieldlineView(Field),)


def get_dynamic_forms_admin_forms():
    return [FieldGroupView(FieldGroup, db.session)]
