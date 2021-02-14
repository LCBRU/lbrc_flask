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
    def _ldap_bind_who_format():
        return current_app.config.get('LDAP_BIND_WHO_FORMAT', None)

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
        current_app.logger.error('A')
        result = None

        try:
            current_app.logger.error('B')
            l = initialize(Ldap._ldap_uri())
            l.protocol_version = 3
            l.set_option(OPT_REFERRALS, 0)

            current_app.logger.error('C')
            l.simple_bind_s(
                Ldap._ldap_user(),
                Ldap._ldap_password(),
            )

            current_app.logger.error('D')
            search_result = l.search_s(
                Ldap._ldap_basedn(),
                SCOPE_SUBTREE,
                search_string,
            )

            current_app.logger.error('E')
            print(search_result)
            if isinstance(search_result[0][1], dict):
                current_app.logger.error('F')
                user = search_result[0][1]
                result = {
                    'username': user['sAMAccountName'][0].decode("utf-8"),
                    'email': user['mail'][0].decode("utf-8"),
                    'name': user['name'][0].decode("utf-8"),
                    'surname': user['sn'][0].decode("utf-8"),
                    'given_name': user['givenName'][0].decode("utf-8"),
                }

            current_app.logger.error('G')

        except LDAPError as e:
            current_app.logger.error('H')
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
        
        finally:
            current_app.logger.error('I')
            return result

    @staticmethod
    def validate_password(user, password):
        current_app.logger.error('1')
        if user is None or not (password or '').strip():
            return False

        current_app.logger.error('2')

        l = initialize(Ldap._ldap_uri())
        l.protocol_version = 3
        l.set_option(OPT_REFERRALS, 0)

        current_app.logger.error('3')
        who = Ldap._ldap_bind_who_format().format(
            user=user,
            basedn=Ldap._ldap_basedn(),
        )

        current_app.logger.error('4')
        try:
            current_app.logger.error('5')
            l.simple_bind_s(
                Ldap._ldap_bind_who_format().format(
                    user=user,
                    basedn=Ldap._ldap_basedn(),
                ),
                password,
            )

            current_app.logger.error('6')

            search_result = l.search_s(
                Ldap._ldap_basedn(),
                SCOPE_SUBTREE,
                who,
            )

            current_app.logger.error('7')

            current_app.logger.error(search_result)

            return True

        except LDAPError as e:
            print(e)
            current_app.logger.error(e)
            return False
