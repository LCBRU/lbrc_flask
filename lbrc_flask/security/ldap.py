from ldap import initialize, SCOPE_SUBTREE, LDAPError, OPT_REFERRALS
import traceback
from flask import current_app


class Ldap():
    def __init__(self):
        self.ldap = None

    def is_enabled(self):
        return len((current_app.config.get('LDAP_URI', None) or '').strip()) > 0

    def login(self, username, password):
        if not (username or '').strip() or not (password or '').strip():
            return False

        self.ldap = initialize(current_app.config.get('LDAP_URI', None))
        self.ldap.protocol_version = 3
        self.ldap.set_option(OPT_REFERRALS, 0)

        try:
            who = current_app.config.get('LDAP_BIND_WHO_FORMAT', None).format(
                username=username,
                basedn=current_app.config.get('LDAP_BASEDN', None),
            )

            self.ldap.simple_bind_s(who, password)

            print('LDAP login Success')

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

            print('LDAP login Success')

            return True

        except LDAPError as e:
            self.ldap = None
            print(e)
            current_app.logger.error(e)
            return False

    def search_username(self, username):
        return self.search(current_app.config.get('LDAP_SEARCH_FORMAT', None).format(username=username))

    def search(self, search_string):
        result = None

        try:
            search_result = self.ldap.search_s(
                current_app.config.get('LDAP_BASEDN', None),
                SCOPE_SUBTREE,
                search_string,
            )

            print('Search Results', search_result)

            if isinstance(search_result[0][1], dict):
                print('User', search_result[0][1])
                user = search_result[0][1]

                result = {
                    'username': user[current_app.config.get('LDAP_FIELDNAME_USERID', None)][0].decode("utf-8"),
                    'email': user[current_app.config.get('LDAP_FIELDNAME_EMAIL', None)][0].decode("utf-8"),
                    'surname': user[current_app.config.get('LDAP_FIELDNAME_GIVENNAME', None)][0].decode("utf-8"),
                    'given_name': user[current_app.config.get('LDAP_FIELDNAME_SURNAME', None)][0].decode("utf-8"),
                }
                print('Result', result)

        except LDAPError as e:
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
        
        finally:
            return result
