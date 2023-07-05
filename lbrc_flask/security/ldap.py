from lbrc_flask.security.model import random_password
from ldap import initialize, SCOPE_SUBTREE, LDAPError, OPT_REFERRALS
import traceback
from flask import current_app
from lbrc_flask.database import db
from flask_security.utils import _datastore

print('Help')
class Ldap():
    def __init__(self):
        print('What the')
        self.ldap = None

    def is_enabled(self):
        return len((current_app.config.get('LDAP_URI', None) or '').strip()) > 0 and current_app.config.get('TESTING', False) == False

    def login(self, username, password):
        if not (username or '').strip() or not (password or '').strip():
            return False

        print('A'*100)
        print(username)

        username = (username or '').strip()
        password = (password or '').strip()

        current_app.logger.info('Attempting login for {}'.format(username))

        try:
            self.ldap = initialize(current_app.config.get('LDAP_URI', None))
            self.ldap.protocol_version = 3
            self.ldap.set_option(OPT_REFERRALS, 0)

            who = current_app.config.get('LDAP_BIND_WHO_FORMAT', None).format(
                username=username,
                basedn=current_app.config.get('LDAP_BASEDN', None),
            )

            print(who)

            self.ldap.simple_bind_s(who, password)

            print('LDAP login Success for {}'.format(username))

            current_app.logger.info('LDAP login Success for {}'.format(username))

            return True

        except LDAPError as e:
            self.ldap = None
            print(e)
            current_app.logger.error(e)
            return False

    def login_nonpriv(self):
        self.ldap = initialize(current_app.config.get('LDAP_URI', None))
        self.ldap.protocol_version = 3
        self.ldap.set_option(OPT_REFERRALS, 0)

        try:
            self.ldap.simple_bind_s(
                current_app.config.get('LDAP_USER', None),
                current_app.config.get('LDAP_PASSWORD', None),
            )

            current_app.logger.info('No Priv LDAP login Success')

            return True

        except LDAPError as e:
            self.ldap = None
            print(e)
            current_app.logger.error(e)
            return False

    def search_username(self, username):
        users = self.search(current_app.config.get('LDAP_SEARCH_FORMAT', None).format(username=username))

        if len(users) != 1:
            return None

        return users[0]

    def search_user(self, search_string):
        return self.search('(|({}=*{}*)({}={}*))'.format(
            current_app.config.get('LDAP_FIELDNAME_FULLNAME', None),
            search_string.strip().replace(' ', '*'),
            current_app.config.get('LDAP_FIELDNAME_USERID', None),
            search_string,
        ))

    def search(self, search_string):
        current_app.logger.info('Searching LDAP for {}'.format(search_string))
        result = []

        try:
            search_result = self.ldap.search_s(
                current_app.config.get('LDAP_BASEDN', None),
                SCOPE_SUBTREE,
                search_string,
            )

            for u in search_result:
                if isinstance(u[1], dict):
                    current_app.logger.info('LDAP found {}'.format(u))
                    result.append({
                        'cn': u[1]['cn'][0].decode("utf-8"),
                        'username': u[1][current_app.config.get('LDAP_FIELDNAME_USERID', None)][0].decode("utf-8"),
                        'email': u[1][current_app.config.get('LDAP_FIELDNAME_EMAIL', None)][0].decode("utf-8"),
                        'given_name': u[1][current_app.config.get('LDAP_FIELDNAME_GIVENNAME', None)][0].decode("utf-8"),
                        'surname': u[1][current_app.config.get('LDAP_FIELDNAME_SURNAME', None)][0].decode("utf-8"),
                    })

            # current_app.logger.info('LDAP found {}'.format(result))

        except LDAPError as e:
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
        
        finally:
            return result

def get_or_create_ldap_user(username):
    ldap = Ldap()

    if ldap.is_enabled():
        username = standardize_username(username)

        ldap.login_nonpriv()

        ldap_user = ldap.search_username(username)

        if ldap_user is not None:
            user = _datastore.find_user(email=ldap_user['email']) or _datastore.find_user(username=ldap_user['username'])

            if not user:
                print('A')
                if current_app.config.get('LDAP_REQUIRE_EXISTING_USER', False):
                    print('B')
                    return None

                print('A')
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

            print(ldap_user['email'])
            print(username)

            return _datastore.find_user(email=ldap_user['email'])


def standardize_username(username):
    result, *_ = username.split('@')
    return result
