from .emailing import init_mail
from .standard_views import init_standard_views


def init_lbrc_flask(app):
    init_mail(app)
    init_standard_views(app)
