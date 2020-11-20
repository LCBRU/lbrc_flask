from flask import Blueprint
from .emailing import init_mail
from .standard_views import init_standard_views
from .template_filters import init_template_filters


def init_lbrc_flask(app):

    blueprint = Blueprint("lbrc_flask", __name__, template_folder="templates", static_folder='static', static_url_path='lbrc_flask/static')
    app.register_blueprint(blueprint)

    init_mail(app)
    init_standard_views(app)
    init_template_filters(app)
