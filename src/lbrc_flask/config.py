import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    ORGANISATION_NAME = os.getenv("ORGANISATION_NAME", "NIHR Leicester BRC")

    # Environment
    TESTING = False
    DEBUG = os.getenv("DEBUG", "False") == 'True'
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", ".")

    # Mail
    SMTP_SERVER = os.getenv("SMTP_SERVER", None)
    MAIL_SERVER = SMTP_SERVER
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "lcbruit@leicester.ac.uk")
    MAIL_REPLY_TO = os.getenv("MAIL_REPLY_TO", None)
    SECURITY_EMAIL_SENDER = os.getenv("SECURITY_EMAIL_SENDER", "lcbruit@leicester.ac.uk")
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", "False") == 'True'

    # Database
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == 'True'
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QUERY_LOG = os.getenv("QUERY_LOG", "False") == 'True'

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", '')
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", SECRET_KEY)
    SECURITY_CONFIRM_SALT = os.getenv("SECURITY_CONFIRM_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_RESET_SALT = os.getenv("SECURITY_RESET_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_LOGIN_SALT = os.getenv("SECURITY_LOGIN_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_REMEMBER_SALT = os.getenv("SECURITY_REMEMBER_SALT", SECURITY_PASSWORD_SALT)
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = os.getenv("SECURITY_SEND_PASSWORD_CHANGE_EMAIL", "False") == 'True'
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_POST_LOGOUT_VIEW = 'ui.index'

    LBRC_FLASK_LOGIN_FORM_DESCRIPTION = os.getenv("LBRC_FLASK_LOGIN_FORM_DESCRIPTION", '')
    LBRC_FLASK_TABLE_BASED_SECURITY = os.getenv("LBRC_FLASK_TABLE_BASED_SECURITY", 'True') == 'True'
    LBRC_UOL_LDAP_SECURITY = os.getenv("LBRC_UOL_LDAP_SECURITY", 'True') == 'True'
    LBRC_UHL_LDAP_SECURITY = os.getenv("LBRC_UHL_LDAP_SECURITY", 'True') == 'True'

    # Users
    ADMIN_EMAIL_ADDRESS = os.getenv("ADMIN_EMAIL_ADDRESS", '')
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", '')
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", None)
    ROLES = os.getenv("ROLES", '')

    # Forms
    WTF_CSRF_ENABLED = True

    # LDAP
    LDAP_REQUIRE_EXISTING_USER = os.getenv("LDAP_REQUIRE_EXISTING_USER", "False") == 'True'
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
    LDAP_NETWORK_NAME = os.getenv("LDAP_NETWORK_NAME", '')

    # Celery
    BROKER_URL = os.getenv("BROKER_URL", '')
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", '')
    CELERY_RATE_LIMIT = os.getenv("CELERY_RATE_LIMIT", '')
    CELERY_REDIRECT_STDOUTS_LEVEL = os.getenv("CELERY_REDIRECT_STDOUTS_LEVEL", '')
    CELERY_DEFAULT_QUEUE = os.getenv("CELERY_DEFAULT_QUEUE", '')
    CELERY_LOG_DIRECTORY = os.getenv("CELERY_LOG_DIRECTORY", ".")



class BaseTestConfig(BaseConfig):
    # Environment
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    LDAP_URI = ''

    # Emails
    SMTP_SERVER = None

    # Security
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

    # Forms
    WTF_CSRF_ENABLED = False
