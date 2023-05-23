from lbrc_flask.security.forms import LbrcChangePasswordForm, LbrcLoginForm, LbrcForgotPasswordForm
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import current_user
from flask import current_app, abort
from flask_security.utils import _datastore
from functools import wraps
from ..database import db
from .model import User, Role, AuditMixin, random_password


def current_user_id():
    return current_user.id

def system_user_id():
    return get_system_user().id


SYSTEM_USER_NAME = 'system'


def get_system_user():
    return _datastore.find_user(username=SYSTEM_USER_NAME)


def get_role_from_name(name):
    return _datastore.find_or_create_role(name=name)


def get_admin_role():
    return get_role_from_name(name=Role.ADMIN_ROLENAME)


def get_user_from_username(username):
    return  _datastore.find_user(username=username)


def get_users_for_role(role_name):
    return  _datastore.user_model.query.join(User.roles).filter(Role.name == role_name).all()


def get_admin_user():
    result =  _datastore.find_user(email=current_app.config["ADMIN_EMAIL_ADDRESS"]) or _datastore.find_user(username=current_app.config["ADMIN_USERNAME"])

    return result


def add_user_to_role(user=None, role=None, username=None, role_name=None):
    if user is None:
        user = get_user_from_username(username)
    
    if role is None:
        role = get_role_from_name(role_name)

    _datastore.add_role_to_user(user, role)


def init_security(app, user_class, role_class):
    user_datastore = SQLAlchemyUserDatastore(db, user_class, role_class)
    Security(
        app,
        user_datastore,
        forgot_password_form=LbrcForgotPasswordForm,
        change_password_form=LbrcChangePasswordForm,
        login_form=LbrcLoginForm,
    )


def init_roles(roles=None):
    if roles is None:
        roles = []

    for r in [Role.ADMIN_ROLENAME] + current_app.config["ROLES"].split(';') + roles:
        if r:
            _datastore.find_or_create_role(
                name=r, description=r
            )


def init_users():
    if not get_system_user():
        user = _datastore.create_user(
            email='hal@discovery_one.uss',
            username=SYSTEM_USER_NAME,
        )

    admin_email = current_app.config["ADMIN_EMAIL_ADDRESS"]
    admin_username = current_app.config["ADMIN_USERNAME"]

    if not _datastore.find_user(email=admin_email) and not _datastore.find_user(username=admin_username):
        print('Creating administrator "{}"'.format(admin_email))
        user = _datastore.create_user(
            email=admin_email,
            username=admin_username,
        )
        _datastore.add_role_to_user(user, get_admin_role())

    db.session.commit()


def must_be_admin():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
