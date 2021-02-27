from lbrc_flask.security.forms import LbrcChangePasswordForm, LbrcLoginForm, LbrcResetPasswordForm
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import current_user
from flask import current_app
from flask_security.utils import _datastore
from ..database import db
from .model import User, Role, AuditMixin


def current_user_id():
    return current_user.id


SYSTEM_USER_NAME = 'system'


def get_system_user():
    return _datastore.find_user(username=SYSTEM_USER_NAME)


def get_admin_user():
    return _datastore.find_user(email=current_app.config["ADMIN_EMAIL_ADDRESS"])


def init_security(app, user_class, role_class):
    user_datastore = SQLAlchemyUserDatastore(db, user_class, role_class)
    Security(
        app,
        user_datastore,
        reset_password_form=LbrcResetPasswordForm,
        change_password_form=LbrcChangePasswordForm,
        login_form=LbrcLoginForm,
    )

    @app.before_first_request
    def init_security():
        init_users()


def init_users():
    admin_role = _datastore.find_or_create_role(
        name=Role.ADMIN_ROLENAME, description=Role.ADMIN_ROLENAME
    )

    if not get_system_user():
        user = _datastore.create_user(
            email='hal@discovery_one.uss',
            username=SYSTEM_USER_NAME,
        )

    admin_email = current_app.config["ADMIN_EMAIL_ADDRESS"]

    if not _datastore.find_user(email=admin_email):
        print('Creating administrator "{}"'.format(admin_email))
        user = _datastore.create_user(
            email=admin_email,
            username=current_app.config["ADMIN_USERNAME"],
        )
        _datastore.add_role_to_user(user, admin_role)

    db.session.commit()
