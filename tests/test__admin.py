from lbrc_flask.admin import AdminCustomView
from lbrc_flask.pytest.helpers import login
from lbrc_flask.database import db
from lbrc_flask.security import User, Role, add_user_to_role


def test__admin__is_admin__is_accessible(client, faker):
    user = faker.user().get(save=True)
    add_user_to_role(user=user, role=Role.get_admin())
    login(client, faker, user)

    out = AdminCustomView(User, db.session)
    
    assert out.is_accessible()


def test__admin__is_not_admin__is_not_accessible(client, faker):
    user = faker.user().get(save=True)
    login(client, faker, user)

    out = AdminCustomView(User, db.session)
    
    assert not out.is_accessible()
