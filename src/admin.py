import flask_admin as admin
from flask import current_app
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView


class AdminCustomView(ModelView):
    def is_accessible(self):
        return current_user.is_admin


def init_admin(app, title, views, url=None, endpoint=None):
    url = url or '/admin'
    flask_admin = admin.Admin(
        app,
        name="{} {}".format(current_app.config["ORGANISATION_NAME"], title),
        url=url,
        endpoint=endpoint,
        template_mode='bootstrap4',
    )

    for v in views:
        flask_admin.add_view(v)
