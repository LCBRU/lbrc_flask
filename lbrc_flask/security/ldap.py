import ldap
from flask import current_app


class Ldap():
    def search():
        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(
                current_app.config['LDAP_USER'],
                current_app.config['LDAP_PASSWORD'],
            )

            search_result = l.search_s(
                'DC=xuhl-tr,DC=nhs,DC=uk',
                ldap.SCOPE_SUBTREE,
                'sAMAccountName={}'.format(self.username),
            )

        except ldap.LDAPError as e:
            log_exception(e)

        if isinstance(search_result[0][1], dict):
            user = search_result[0][1]
            return {
                'username': user['sAMAccountName'][0].decode("utf-8"),
                'email': user['mail'][0].decode("utf-8"),
                'name': user['name'][0].decode("utf-8"),
                'surname': user['sn'][0].decode("utf-8"),
                'given_name': user['givenName'][0].decode("utf-8"),
            }
        else:
            return {
                'username': self.username,
                'email': '',
                'name': '',
                'surname': self.last_name,
                'given_name': self.first_name,
            }

    def validate_password(self, password):
        if current_app.config['TESTING']:
            return True

        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(self.email, password)
            return True

        except ldap.LDAPError as e:
            print(e)
            return False
