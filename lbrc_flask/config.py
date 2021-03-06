import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    # Environment
    TESTING = False
    DEBUG = os.getenv("DEBUG", "False") == 'True'
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", ".")

    # Mail
    SMTP_SERVER = os.getenv("SMTP_SERVER", None)
    MAIL_SERVER = SMTP_SERVER
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "lcbruit@leicester.ac.uk")
    SECURITY_EMAIL_SENDER = os.getenv("SECURITY_EMAIL_SENDER", "lcbruit@leicester.ac.uk")
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", "False") == 'True'

    # Database
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ["SECRET_KEY"]
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email', 'username']
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", SECRET_KEY)
    SECURITY_CONFIRM_SALT = os.getenv("SECURITY_CONFIRM_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_RESET_SALT = os.getenv("SECURITY_RESET_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_LOGIN_SALT = os.getenv("SECURITY_LOGIN_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_REMEMBER_SALT = os.getenv("SECURITY_REMEMBER_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = os.getenv("SECURITY_SEND_PASSWORD_CHANGE_EMAIL", "False") == 'True'
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True

    # Users
    ADMIN_EMAIL_ADDRESS = os.getenv("ADMIN_EMAIL_ADDRESS", '')
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", '')

    # Forms
    WTF_CSRF_ENABLED = True

    # LDAP
    LDAP_URI = os.getenv("LDAP_URI", '')
    LDAP_USER = os.getenv("LDAP_USER", '')
    LDAP_PASSWORD = os.getenv("LDAP_PASSWORD", '')
    LDAP_BASEDN = os.getenv("LDAP_BASEDN", '')
    LDAP_BIND_WHO_FORMAT = os.getenv("LDAP_BIND_WHO_FORMAT", '')
    LDAP_SEARCH_FORMAT = os.getenv("LDAP_SEARCH_FORMAT", '')
    LDAP_FIELDNAME_USERID = os.getenv("LDAP_FIELDNAME_USERID", '')
    LDAP_FIELDNAME_EMAIL = os.getenv("LDAP_FIELDNAME_EMAIL", '')
    LDAP_FIELDNAME_GIVENNAME = os.getenv("LDAP_FIELDNAME_GIVENNAME", '')
    LDAP_FIELDNAME_SURNAME = os.getenv("LDAP_FIELDNAME_SURNAME", '')
    LDAP_FIELDNAME_FULLNAME = os.getenv("LDAP_FIELDNAME_FULLNAME", '')
    LDAP_TEST_USER = os.getenv("LDAP_TEST_USER", '')


class BaseTestConfig(BaseConfig):
    # Environment
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    # Emails
    SMTP_SERVER = None

    # Security
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

    # Forms
    WTF_CSRF_ENABLED = False
