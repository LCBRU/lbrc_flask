from lbrc_flask.pytest.helpers import login
from lbrc_flask.security import AuditMixin


class ObjectUnserTest(AuditMixin):
    pass


def test__audit_mixin__current_user(client, faker):
    user = login(client, faker)

    out = ObjectUnserTest()

    assert out.current_user_email() == user.email


def test__audit_mixin__current_user__not_logged_in(client, faker):
    out = ObjectUnserTest()

    assert out.current_user_email() == '[None]'
