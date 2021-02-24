from lbrc_flask.security.forms import LbrcChangePasswordForm, LbrcLoginForm, LbrcResetPasswordForm
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import current_user
from ..database import db
from .model import User, Role, AuditMixin


def current_user_id():
    return current_user.id


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
        admin_role = user_datastore.find_or_create_role(
            name=role_class.ADMIN_ROLENAME, description=role_class.ADMIN_ROLENAME
        )

        admin_email = app.config["ADMIN_EMAIL_ADDRESS"]

        if not user_datastore.find_user(email=admin_email):
            print('Creating administrator "{}"'.format(admin_email))
            user = user_datastore.create_user(
                email=admin_email,
                username=app.config["ADMIN_USERNAME"],
            )
            user_datastore.add_role_to_user(user, admin_role)

        db.session.commit()
