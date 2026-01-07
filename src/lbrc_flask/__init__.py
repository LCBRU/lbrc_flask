from flask import Blueprint, g
from .database import db
from .emailing import init_mail
from .standard_views import init_standard_views
from .template_filters import init_template_filters
from .logging import init_logging
from rich.traceback import install
from setproctitle import setproctitle


install(show_locals=True)


blueprint = Blueprint("lbrc_flask", __name__, template_folder="templates", static_folder='static', url_prefix='/lbrc_flask')


def init_lbrc_flask(app, title):
    setproctitle(f'{title}-Flask')
    app.register_blueprint(blueprint)

    init_logging(app)
    db.init_app(app)
    init_mail(app)
    init_standard_views(app)
    init_template_filters(app)

    @app.before_request
    def get_current_user():
        g.lbrc_flask_title = title


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.
    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }
    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server

        return self.app(environ, start_response)
