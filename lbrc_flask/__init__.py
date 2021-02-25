from flask import Blueprint, g
from .database import db
from .emailing import init_mail
from .standard_views import init_standard_views
from .template_filters import init_template_filters
from .logging import init_logging


blueprint = Blueprint("lbrc_flask", __name__, template_folder="templates", static_folder='static', url_prefix='/lbrc_flask')


def init_lbrc_flask(app, title):

    app.register_blueprint(blueprint)

    init_logging(app)
    db.init_app(app)
    init_mail(app)
    init_standard_views(app)
    init_template_filters(app)

    @app.before_request
    def get_current_user():
        g.lbrc_flask_title = title