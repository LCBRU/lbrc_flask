import flask_admin as admin
from flask import current_app, abort, redirect, url_for, request
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView


class AdminCustomView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role("superuser")
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
