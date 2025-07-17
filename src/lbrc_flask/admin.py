from flask_admin import AdminIndexView, Admin, expose
from flask import current_app, abort, redirect, url_for, request
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView
from flask_security import roles_accepted


class AdminCustomView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role("admin")
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not
        accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for("security.login", next=request.url))


class AdminHomeView(AdminIndexView):
    @roles_accepted('admin')
    @expose('/')
    def index(self):
        return super().index()


def init_admin(app, title, views, url=None, endpoint=None):
    url = url or '/admin'
    flask_admin = Admin(
        app,
        name="{} {}".format(current_app.config["ORGANISATION_NAME"], title),
        url=url,
        endpoint=endpoint,
        theme=Bootstrap4Theme(swatch='cerulean')
        index_view=AdminHomeView()
    )

    for v in views:
        flask_admin.add_view(v)
