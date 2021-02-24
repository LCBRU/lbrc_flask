import os
import traceback
from flask import render_template, send_from_directory, current_app, g
from .emailing import email


def init_standard_views(app):
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.errorhandler(404)
    def missing_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 404

    @app.errorhandler(403)
    def forbidden_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("lbrc_flask/404.html"), 403

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

        print(traceback.format_exc())
        app.logger.error(traceback.format_exc())
        email(
            subject="NIHR Leicester BRC {} Error".format(app_name),
            message=traceback.format_exc(),
            recipients=[current_app.config["ADMIN_EMAIL_ADDRESS"]],
        )
        return render_template("lbrc_flask/500.html"), 500
