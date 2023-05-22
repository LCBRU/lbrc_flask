import random
import string
from datetime import datetime
from flask_security.core import RoleMixin, UserMixin
from flask_security.utils import verify_and_update_password
from flask_login import current_user
from sqlalchemy.ext.declarative import declared_attr
from lbrc_flask.model import CommonMixin
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


class Role(db.Model, RoleMixin, CommonMixin):
    ADMIN_ROLENAME = "admin"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __str__(self):
        return self.name or ""

    @staticmethod
    def get_admin():
        return Role.query.filter(Role.name == Role.ADMIN_ROLENAME).one()


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class User(db.Model, CommonMixin, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False, default=random_password)
    first_name = db.Column(db.String(255), default='')
    last_name = db.Column(db.String(255), default='')
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer())
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ldap_user = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship(
        "Role",
        lazy="joined",
        enable_typechecks=False,    # Required to allow specific applications
                                    # to override the Role class
        secondary=roles_users,
        # collection_class=set,
        backref=db.backref(
            "users",
            lazy="dynamic",
            enable_typechecks=False,    # Required to allow specific applications
                                        # to override the User class
        ),
    )

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.has_role(Role.ADMIN_ROLENAME)

    @property
    def full_name(self):
        full_name = " ".join(filter(None, [self.first_name, self.last_name]))

        return full_name or self.email or ''

    def __str__(self):
        return self.full_name

    def verify_and_update_password(self, password):
        # First try to Ldap, then locally
        # ldap = Ldap()

        # if ldap.is_enabled():
        #     if ldap.login(self, password):
        #         user_details = ldap.search_email(self.email)
        #         return True

        return verify_and_update_password(password, self)
