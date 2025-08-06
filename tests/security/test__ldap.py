import ldap3 as ldap_lib
from lbrc_flask.security.ldap import Ldap
from flask import current_app


def test__ldap__is_enable__nouri(client, faker):
    current_app.config['LDAP_URI'] = ''

    ldap = Ldap()
    assert ldap.is_enabled() == False


def test__ldap__is_enable__withuri(client, faker):
    current_app.config['LDAP_URI'] = faker.pystr(min_chars=5, max_chars=10)
    current_app.config['TESTING'] = False

    ldap = Ldap()
    assert ldap.is_enabled()


def test__ldap__validate_password__user_none(client, faker):
    ldap = Ldap()
    assert ldap.login(None, faker.pystr(min_chars=5, max_chars=10)) == False


def test__ldap__validate_password__password_none(client, faker):
    ldap = Ldap()
    assert ldap.login(faker.pystr(min_chars=5, max_chars=10), None) == False


def test__ldap__validate_password__password_empty(client, faker):
    ldap = Ldap()
    assert ldap.login(faker.pystr(min_chars=5, max_chars=10), '') == False


def test__ldap__validate_password__password_blank(client, faker):
    ldap = Ldap()
    assert ldap.login(faker.pystr(min_chars=5, max_chars=10), '   ') == False
