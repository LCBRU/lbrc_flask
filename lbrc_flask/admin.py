import flask_admin as admin
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView


class AdminCustomView(ModelView):
    def is_accessible(self):
        return current_user.is_admin


def init_admin(app, title, views):
    flask_admin = admin.Admin(app, name="NIHR Leicester BRC {}".format(title), url="/admin", template_mode='bootstrap4')

    for v in views:
        flask_admin.add_view(v)
