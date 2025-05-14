from lbrc_flask.security.model import random_password
import traceback
import ssl
from flask import current_app
from lbrc_flask.database import db
from flask_security.utils import _datastore
from ldap3.core.exceptions import LDAPException
from ldap3 import ALL, Connection, Server, Tls, SUBTREE


class Ldap():
    def __init__(self):
        self.connection = None
        self.URI = (current_app.config.get('LDAP_URI', None) or '').strip()
        self.BIND_WHO_FORMAT = (current_app.config.get('LDAP_BIND_WHO_FORMAT', None) or '').strip()
        self.BASEDN = (current_app.config.get('LDAP_BASEDN', None) or '').strip()
        self.NOPRIV_USER = (current_app.config.get('LDAP_USER', None) or '').strip()
        self.NONPRIV_PASSWORD = (current_app.config.get('LDAP_PASSWORD', None) or '').strip()
        self.USERNAME_SEARCH_FORMAT = (current_app.config.get('LDAP_SEARCH_FORMAT', None) or '').strip()

        self.FIELDNAME_FULLNAME = (current_app.config.get('LDAP_FIELDNAME_FULLNAME', None) or '').strip()
        self.FIELDNAME_USERID = (current_app.config.get('LDAP_FIELDNAME_USERID', None) or '').strip()
        self.FIELDNAME_EMAIL = (current_app.config.get('LDAP_FIELDNAME_EMAIL', None) or '').strip()
        self.FIELDNAME_GIVEN_NAME = (current_app.config.get('LDAP_FIELDNAME_GIVENNAME', None) or '').strip()
        self.FIELDNAME_SURNAME = (current_app.config.get('LDAP_FIELDNAME_SURNAME', None) or '').strip()

    def is_enabled(self):
        ldap_uri_set = len(self.URI) > 0
        not_testing = not current_app.config.get('TESTING', False)
        return ldap_uri_set and not_testing

    def login(self, username, password):
        username = (username or '').strip()
        password = (password or '').strip()

        if not username:
            current_app.logger.info("Login Invalid: Username empty")
            return False
        if not password:
            current_app.logger.info("Login Invalid: Password empty")
            return False

        current_app.logger.info(f"Attempting login for '{username}'")

        bind_user_details = self.BIND_WHO_FORMAT.format(
            username=username,
            basedn=self.BASEDN,
        )

        if self._login_bind_user(bind_user_details, password):
            current_app.logger.info(f"LDAP login Success for '{username}'")
            return True
        else:
            current_app.logger.info(f"LDAP login Failed for '{username}'")
            return False


    def _login_bind_user(self, bind_user, password):
        try:
            tls = Tls(version=ssl.PROTOCOL_TLS, ciphers='ALL')
            server = Server(
                host="ldap.rcs.le.ac.uk",
                port=636,
                use_ssl=True,
                tls=tls,
                get_info=ALL,
            )

            self.connection = Connection(
                server,
                user=bind_user,
                password=password,
                auto_bind=True,
                auto_referrals=False,
            )

            return True

        except LDAPException as e:
            print(e)
            current_app.logger.error(e)
            return False

    def login_nonpriv(self):
        if self._login_bind_user(self.NOPRIV_USER, self.NONPRIV_PASSWORD):
            current_app.logger.info("LDAP login Success Non-Privileged user")
            return True
        else:
            current_app.logger.info("LDAP login Failed for Non-Privileged user")
            return False
    
    def search_username(self, username):
        q = self.USERNAME_SEARCH_FORMAT.format(username=username)
        users = self.search(q)

        print(users)

        if len(users) == 0:
            current_app.logger.info(f"No user found for username '{username}'")
            return None

        result = users[0]
        current_app.logger.info(f"Found user '{result}' for username '{username}'")

        return result

    def search_user(self, search_string):
        search_string = search_string.strip()
        wildcard_search_string = search_string.strip().replace(' ', '*')

        q = f"(|({self.FIELDNAME_FULLNAME}=*{wildcard_search_string}*)({self.FIELDNAME_USERID}={search_string}*))"

        return self.search(q)

    def search(self, search_query):
        current_app.logger.info(f"Searching LDAP for {search_query}")
        result = []

        try:
            self.connection.search(
                self.BASEDN,
                search_query,
                search_scope=SUBTREE,
                attributes=[
                    self.FIELDNAME_USERID,
                    self.FIELDNAME_EMAIL,
                    self.FIELDNAME_GIVEN_NAME,
                    self.FIELDNAME_SURNAME,
                ]
            )

            for user in self.connection.entries:
                current_app.logger.info(f"LDAP found {user}")
                print('#######', user[self.FIELDNAME_USERID])
                result.append({
                    'username': user[self.FIELDNAME_USERID],
                    'email': user[self.FIELDNAME_EMAIL],
                    'given_name': user[self.FIELDNAME_GIVEN_NAME],
                    'surname': user[self.FIELDNAME_SURNAME],
                })

        except Exception as e:
            current_app.logger.error(traceback.format_exc())

        return result

def get_or_create_ldap_user(username):
    ldap = Ldap()

    if ldap.is_enabled():
        username = standardize_username(username)

        ldap.login_nonpriv()

        ldap_user = ldap.search_username(username)
        current_app.logger.info(f"User '{ldap_user}' found for '{username}'")

        if ldap_user is not None:
            current_app.logger.info(f"LDAP user '{username}' found.  Attempting to find user in user table")
            user = _datastore.find_user(email=ldap_user['email']) or _datastore.find_user(username=ldap_user['username'])

            if not user:
                current_app.logger.info(f"'{username}' not found is user table")
                if current_app.config.get('LDAP_REQUIRE_EXISTING_USER', False):
                    current_app.logger.info("Existing user required so not creating one")
                    return None

                current_app.logger.info(f"Creating user table record for LDAP user '{username}'")
                user = _datastore.create_user(
                    email=ldap_user['email'],
                    password=random_password(),
                )

            current_app.logger.info(f"Updating user table details from LDAP record for user '{username}'")
            user.email = ldap_user['email']
            user.username = ldap_user['username']
            user.first_name = ldap_user['given_name']
            user.last_name = ldap_user['surname']
            user.ldap_user = True
            
            db.session.add(user)
            db.session.commit()

            return _datastore.find_user(email=ldap_user['email'])


def standardize_username(username):
    result, *_ = username.split('@')
    return result
