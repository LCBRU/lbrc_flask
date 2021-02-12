from ldap import initialize, SCOPE_SUBTREE, LDAPError, OPT_REFERRALS
import traceback
from flask import current_app


class Ldap():
    @staticmethod
    def _ldap_uri():
        return current_app.config.get('LDAP_URI', None)

    @staticmethod
    def _ldap_user():
        return current_app.config.get('LDAP_USER', None)

    @staticmethod
    def _ldap_password():
        return current_app.config.get('LDAP_PASSWORD', None)

    @staticmethod
    def _ldap_basedn():
        return current_app.config.get('LDAP_BASEDN', None)

    @staticmethod
    def is_enabled():
        return len((Ldap._ldap_uri() or '').strip()) > 0

    @staticmethod
    def search_username(username):
        return Ldap.search('sAMAccountName={}'.format(username))

    @staticmethod
    def search_email(email):
        return Ldap.search('(mail={})'.format(email))

    @staticmethod
    def search(search_string):
        result = None

        try:
            l = initialize(Ldap._ldap_uri())
            l.protocol_version = 3
            l.set_option(OPT_REFERRALS, 0)

            l.simple_bind_s(
                Ldap._ldap_user(),
                Ldap._ldap_password(),
            )

            search_result = l.search_s(
                Ldap._ldap_basedn(),
                SCOPE_SUBTREE,
                search_string,
            )

            if isinstance(search_result[0][1], dict):
                user = search_result[0][1]
                result = {
                    'username': user['sAMAccountName'][0].decode("utf-8"),
                    'email': user['mail'][0].decode("utf-8"),
                    'name': user['name'][0].decode("utf-8"),
                    'surname': user['sn'][0].decode("utf-8"),
                    'given_name': user['givenName'][0].decode("utf-8"),
                }

        except LDAPError as e:
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
        
        finally:
            return result

    @staticmethod
    def validate_password(username, password):
        if not (username or '').strip() or not (password or '').strip():
            return False

        l = initialize(Ldap._ldap_uri())
        l.protocol_version = 3
        l.set_option(OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(username, password)
            return True

        except LDAPError as e:
            print(e)
            current_app.logger.error(e)
            return False
