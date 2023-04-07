from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.security import system_user_id
from flask_api import status


def test__security__get_user_id(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('user_id'))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == user.id


def test__security__get_system_user_id(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('get_system_user_id'))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == 1


def test__security__user_id_for_username(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('user_id_for_username', username=user.username))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == user.id


def test__security__admin_user_id(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('admin_user_id'))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == 2


def test__security__users_in_role__none(client, faker):
    user = login(client, faker)
    role = faker.get_test_role()

    resp = client.get(url_for('users_for_role', rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == ''


def test__security__users_in_role__one(client, faker):
    user = login(client, faker)
    role = faker.get_test_role()
    u2 = faker.get_test_user()

    resp = client.get(url_for('add_username_to_rolename', username=u2.username, rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK
    resp = client.get(url_for('users_for_role', rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == f'{u2.id}'


def test__security__users_in_role__two(client, faker):
    user = login(client, faker)
    role = faker.get_test_role()
    u2 = faker.get_test_user()
    u3 = faker.get_test_user()

    resp = client.get(url_for('add_username_to_rolename', username=u2.username, rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK
    resp = client.get(url_for('add_username_to_rolename', username=u3.username, rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK
    resp = client.get(url_for('users_for_role', rolename=role.name))
    assert resp.status_code == status.HTTP_200_OK

    assert resp.get_json()['result'] == f'{u2.id},{u3.id}'


def test__security__must_be_an_admin__isnt(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('must_be_an_admin'))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test__security__must_be_an_admin__is(client, faker):
    u = faker.get_test_user(is_admin=True)
    user = login(client, faker, user=u)

    resp = client.get(url_for('must_be_an_admin'))
    assert resp.status_code == status.HTTP_200_OK


