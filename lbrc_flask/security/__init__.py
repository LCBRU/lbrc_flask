import random
import string
from datetime import datetime
from flask.globals import current_app
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.core import RoleMixin, UserMixin
from flask_security.forms import (
    EqualTo,
    password_length,
    password_required,
    get_form_field_label,
    ValidatorMixin,
    Form,
    PasswordFormMixin,
)
from flask_security.utils import verify_and_update_password, get_message
from flask_login import current_user
from wtforms.validators import ValidationError
from wtforms import PasswordField, SubmitField
from sqlalchemy.ext.declarative import declared_attr
from ..database import db


class AuditMixin(object):

    @staticmethod
    def current_user_email():
        if current_user and hasattr(current_user, 'email'):
            return current_user.email
        else:
            return '[None]'

    last_update_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @declared_attr
    def last_update_by(cls):
        return db.Column(
            db.String,
            nullable=False,
            default=AuditMixin.current_user_email,
            onupdate=AuditMixin.current_user_email,
        )


    created_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    @declared_attr
    def created_by(cls):
        return db.Column(
            db.String,
            nullable=False,
            default=AuditMixin.current_user_email,
        )

def random_password():
    return "".join(
        random.SystemRandom().choice(
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
            + string.punctuation
        )
        for _ in range(15)
    )


class Role(db.Model, RoleMixin):
    ADMIN_ROLENAME = "admin"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __str__(self):
        return self.name or ""


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False, default=random_password)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer())
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    roles = db.relationship(
        "Role",
        enable_typechecks=False, # Required to allow specific applications
                                 # to override the Role class
        secondary=roles_users,
        backref=db.backref(
            "users",
            lazy="dynamic",
            enable_typechecks=False, # Required to allow specific applications
                                     # to override the User class
        ),
    )

    @property
    def is_admin(self):
        return self.has_role(Role.ADMIN_ROLENAME)

    @property
    def full_name(self):
        full_name = " ".join(filter(None, [self.first_name, self.last_name]))

        return full_name or self.email

    def __str__(self):
        return self.email


class PasswordPolicy(ValidatorMixin):
    def __init__(
        self,
        message=u"The password must contain a lowercase, "
        "uppercase and punctuation character",
    ):
        self.message = message

    def __call__(self, form, field):
        value = set(field.data)

        if (
            value.isdisjoint(string.ascii_lowercase)
            or value.isdisjoint(string.ascii_uppercase)
            or value.isdisjoint(string.punctuation)
        ):
            raise ValidationError(self.message)


class NewPasswordFormMixin:
    password = PasswordField(
        get_form_field_label("password"),
        validators=[password_required, password_length, PasswordPolicy()],
    )


class PasswordConfirmFormMixin:
    password_confirm = PasswordField(
        get_form_field_label("retype_password"),
        validators=[
            EqualTo("password", message="RETYPE_PASSWORD_MISMATCH"),
            password_required,
        ],
    )


class ResetPasswordForm(Form, NewPasswordFormMixin, PasswordConfirmFormMixin):
    """The default reset password form"""

    submit = SubmitField(get_form_field_label("reset_password"))


class ChangePasswordForm(Form, PasswordFormMixin):
    """The default change password form"""

    new_password = PasswordField(
        get_form_field_label("new_password"),
        validators=[password_required, password_length, PasswordPolicy()],
    )

    new_password_confirm = PasswordField(
        get_form_field_label("retype_password"),
        validators=[
            EqualTo("new_password", message="RETYPE_PASSWORD_MISMATCH"),
            password_required,
        ],
    )

    submit = SubmitField(get_form_field_label("change_password"))

    def validate(self):
        if not super(ChangePasswordForm, self).validate():
            return False

        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append(get_message("INVALID_PASSWORD")[0])
            return False
        if self.password.data.strip() == self.new_password.data.strip():
            self.password.errors.append(get_message("PASSWORD_IS_THE_SAME")[0])
            return False
        return True


def init_security(app, user_class, role_class):
    user_datastore = SQLAlchemyUserDatastore(db, user_class, role_class)
    Security(
        app,
        user_datastore,
        reset_password_form=ResetPasswordForm,
        change_password_form=ChangePasswordForm,
    )

    @app.before_first_request
    def init_security():
        admin_role = user_datastore.find_or_create_role(
            name=role_class.ADMIN_ROLENAME, description=role_class.ADMIN_ROLENAME
        )

        for a in app.config["ADMIN_EMAIL_ADDRESSES"].split(";"):
            if not user_datastore.find_user(email=a):
                print('Creating administrator "{}"'.format(a))
                user = user_datastore.create_user(email=a)
                user_datastore.add_role_to_user(user, admin_role)

        db.session.commit()
