from lbrc_flask.admin import AdminCustomView
from flask_admin.model.form import InlineFormAdmin
from wtforms import validators
from wtforms.validators import Length, DataRequired, Optional, Regexp
from flask_wtf.file import FileAllowed
from lbrc_flask.database import db
from . import DescriptionField, FlashingForm


class FieldType(db.Model):

    BOOLEAN = 'BooleanField'
    INTEGER = 'IntegerField'
    RADIO = 'RadioField'
    STRING = 'StringField'
    TEXTAREA = 'TextAreaField'
    FILE = 'FileField'
    MULTIPLE_FILE = 'MultipleFileField'
    DESCRIPTION = 'DescriptionField'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)
    is_file = db.Column(db.Boolean)

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

    def _add_field_type(self, field_type):
        if FieldType.query.filter_by(name=field_type.name).count() == 0:
            db.session.add(field_type)


class FieldGroup(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)

    def __str__(self):
        return self.name


class Field(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    field_group_id = db.Column(db.Integer(), db.ForeignKey(FieldGroup.id))
    field_group = db.relationship(FieldGroup, backref='fields')
    order = db.Column(db.Integer())
    field_type_id = db.Column(db.Integer(), db.ForeignKey(FieldType.id))
    field_type = db.relationship(FieldType)
    field_name = db.Column(db.String)
    label = db.Column(db.String)
    required = db.Column(db.Boolean, default=0)
    max_length = db.Column(db.Integer(), default=0)
    default = db.Column(db.String, default="")
    choices = db.Column(db.String, default="")
    allowed_file_extensions = db.Column(db.String, default="")
    download_filename_format = db.Column(db.String, default="")
    validation_regex = db.Column(db.String, default="")
    description = db.Column(db.UnicodeText, default="")

    def get_default(self):
        if self.default == '':
            return None
        else:
            return self.default

    def get_choices(self):
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
            self.order, self.field_name, self.field_type.name
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

        return DynamicForm()
    
    def add_field_group(self, field_group):
        for f in field_group.fields:
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

        if field.field_type == FieldType.get_description():
            form_field = DescriptionField(field.get_label(), description=field.description, **kwargs)
        else:
            module = __import__("wtforms")
            class_ = getattr(module, field.field_type.name)
            form_field = class_(field.get_label(), **kwargs)

        self._fields[field.field_name] = form_field


# Initialisation

def init_dynamic_forms(app):
    
    @app.before_first_request
    def init_data():
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
