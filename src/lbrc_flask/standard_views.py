import os
import traceback
from flask import render_template, send_from_directory, current_app, g
from lbrc_flask.logging import log_exception
from .emailing import email


def init_standard_views(app):
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.errorhandler(400)
    def missing_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 400

    @app.errorhandler(401)
    def missing_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 401

    @app.errorhandler(403)
    def forbidden_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 403

    @app.errorhandler(404)
    def missing_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 404

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_error(exception):
        """Catch internal exceptions and 500 errors, display
            a nice error page and log the error.
        """
        if 'lbrc_flask_title' in g:
            app_name = g.lbrc_flask_title
        else:
            app_name = 'Application'

        log_exception(exception)

        return render_template("lbrc_flask/500.html"), 500
