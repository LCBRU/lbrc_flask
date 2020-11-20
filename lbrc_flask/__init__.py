from .emailing import init_mail
from .standard_views import init_standard_views
from .template_filters import init_template_filters


def init_lbrc_flask(app):
    init_mail(app)
    init_standard_views(app)
    init_template_filters(app)
