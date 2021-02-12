import ldap as ldap_lib
from lbrc_flask.security.ldap import Ldap
from flask import current_app


def test__ldap__is_enable__nouri(client, faker, ldap_initialize):
    current_app.config['LDAP_URI'] = ''

    assert Ldap.is_enabled() == False


def test__ldap__is_enable__withuri(client, faker, ldap_initialize):
    current_app.config['LDAP_URI'] = faker.pystr(min_chars=5, max_chars=10)

    assert Ldap.is_enabled()


def test__ldap__validate_password__username_none(client, faker, ldap_initialize):
    assert Ldap.validate_password(None, faker.pystr(min_chars=5, max_chars=10)) == False


def test__ldap__validate_password__username_empty(client, faker, ldap_initialize):
    assert Ldap.validate_password('', faker.pystr(min_chars=5, max_chars=10)) == False


def test__ldap__validate_password__username_blank(client, faker, ldap_initialize):
    assert Ldap.validate_password('    ', faker.pystr(min_chars=5, max_chars=10)) == False


def test__ldap__validate_password__password_none(client, faker, ldap_initialize):
    assert Ldap.validate_password(faker.pystr(min_chars=5, max_chars=10), None) == False


def test__ldap__validate_password__password_empty(client, faker, ldap_initialize):
    assert Ldap.validate_password(faker.pystr(min_chars=5, max_chars=10), '') == False


def test__ldap__validate_password__password_blank(client, faker, ldap_initialize):
    assert Ldap.validate_password(faker.pystr(min_chars=5, max_chars=10), '   ') == False


def test__ldap__validate_password__valid(client, faker, ldap_initialize):
    assert Ldap.validate_password(faker.pystr(min_chars=5, max_chars=10), faker.pystr(min_chars=5, max_chars=10))


def test__ldap__validate_password__bind_fails(client, faker, ldap_initialize):
    ldap_initialize.return_value.simple_bind_s.side_effect = ldap_lib.LDAPError

    assert Ldap.validate_password(faker.pystr(min_chars=5, max_chars=10), faker.pystr(min_chars=5, max_chars=10)) == False

