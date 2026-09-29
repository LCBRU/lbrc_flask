import os

from flask import render_template, send_from_directory

from lbrc_flask.logging import log_exception

from .database import db


def init_standard_views(app):
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.errorhandler(400)
    def bad_request(exception):
        return render_template("lbrc_flask/404.html"), 400

    @app.errorhandler(401)
    def unauthorized(exception):
        return render_template("lbrc_flask/404.html"), 401

    @app.errorhandler(403)
    def forbidden(exception):
        return render_template("lbrc_flask/404.html"), 403

    @app.errorhandler(404)
    def not_found(exception):
        return render_template("lbrc_flask/404.html"), 404

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_error(exception):

        db.session.rollback()

        log_exception(exception)

        return render_template("lbrc_flask/500.html"), 500
