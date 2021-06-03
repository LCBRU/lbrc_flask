from lbrc_flask.security.model import random_password
from lbrc_flask.security.ldap import Ldap
import string
from flask_security.forms import (
    EqualTo,
    password_length,
    password_required,
    get_form_field_label,
    ValidatorMixin,
    Form,
    PasswordFormMixin,
)
from flask_security.utils import verify_and_update_password, get_message, _datastore
from flask_login import current_user
from wtforms.validators import ValidationError
from wtforms import PasswordField, SubmitField
from flask_security.forms import LoginForm
from lbrc_flask.database import db


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


class LbrcResetPasswordForm(Form, NewPasswordFormMixin, PasswordConfirmFormMixin):
    """The default reset password form"""

    submit = SubmitField(get_form_field_label("reset_password"))


class LbrcChangePasswordForm(Form, PasswordFormMixin):
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
        if not super(LbrcChangePasswordForm, self).validate():
            return False

        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append(get_message("INVALID_PASSWORD")[0])
            return False
        if self.password.data.strip() == self.new_password.data.strip():
            self.password.errors.append(get_message("PASSWORD_IS_THE_SAME")[0])
            return False
        return True


class LbrcLoginForm(LoginForm):
    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        ldap = Ldap()

        if ldap.is_enabled():
            username = self._standardize_username(self.email.data)

            if ldap.login(username, self.password.data):
                ldap_users = ldap.search_username(username)

                # GUARD: Even if they've managed to login, if we can't get the
                #        user details we're not letting 'em in.  It's probably
                #        a config error, but it's probably safer to deny entry.
                if len(ldap_users) != 1:
                    return False

                ldap_user = ldap_users[0]

                user = _datastore.find_user(email=ldap_user['email']) or _datastore.find_user(username=ldap_user['username'])

                if not user:
                    user = _datastore.create_user(
                        email=ldap_user['email'],
                        password=random_password(),
                    )

                user.email = ldap_user['email']
                user.username = ldap_user['username']
                user.first_name = ldap_user['given_name']
                user.last_name = ldap_user['surname']
                user.ldap_user = True
                
                db.session.add(user)
                db.session.commit()

                self.user = _datastore.get_user(ldap_user['email'])

                return True

        return super().validate()

    def _standardize_username(self, username):
        result, *_ = username.split('@')
        return result
