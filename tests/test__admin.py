from lbrc_flask.admin import AdminCustomView, init_admin
from lbrc_flask.pytest.helpers import login
from lbrc_flask.database import db
from lbrc_flask.security import User, Role


def test__admin__is_admin__is_accessible(client, faker):
    user = faker.get_test_user(is_admin=True)
    login(client, faker, user)

    out = AdminCustomView(User, db.session)
    
    assert out.is_accessible()


def test__admin__is_not_admin__is_not_accessible(client, faker):
    user = faker.get_test_user()
    login(client, faker, user)

    out = AdminCustomView(User, db.session)
    
    assert not out.is_accessible()


def test__admin__init_admin__loads_views(app):
    views = [
        AdminCustomView(User, db.session),
        AdminCustomView(Role, db.session),
    ]

    with app.app_context():
        init_admin(app, 'Test', views)
